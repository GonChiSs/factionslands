package com.factionlands;

import java.util.Optional;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;

/** Funda una civilización completa (la plantilla de aldea de la facción) sobre el terreno, aplanándolo. */
public final class Civilizations {
	/** Capa de suelo dentro de la plantilla (tools/builders.py: F = 2); el bloque pulsado pasa a ser esa capa. */
	private static final int FLOOR = 2;
	/** Bloques extra por encima de la plantilla que se despejan (árboles, colinas). */
	private static final int CLEAR_EXTRA = 4;
	/** Profundidad máxima del relleno de tierra bajo la aldea cuando el terreno tiene huecos. */
	private static final int SKIRT_DEPTH = 12;

	public record Result(boolean ok, Component message) {}

	/** La aldea se orienta hacia donde mira quien la funda. */
	public static Rotation rotationFor(Direction facing) {
		return switch (facing) {
			case EAST -> Rotation.CLOCKWISE_90;
			case SOUTH -> Rotation.CLOCKWISE_180;
			case WEST -> Rotation.COUNTERCLOCKWISE_90;
			default -> Rotation.NONE;
		};
	}

	/** Misma transformación que StructureTemplate con pivote (0,0). */
	private static int[] rotate(int x, int z, Rotation r) {
		return switch (r) {
			case CLOCKWISE_90 -> new int[] {-z, x};
			case CLOCKWISE_180 -> new int[] {-x, -z};
			case COUNTERCLOCKWISE_90 -> new int[] {z, -x};
			default -> new int[] {x, z};
		};
	}

	/**
	 * @param ground bloque de suelo sobre el que se centra la aldea (su capa pasa a ser la calle)
	 */
	public static Result found(ServerLevel level, BlockPos ground, Rotation rotation, Faction faction) {
		Optional<StructureTemplate> found = level.getStructureTemplateManager()
				.get(FactionLands.id(faction.id + "/village"));
		if (found.isEmpty()) {
			return new Result(false, Component.translatable("message.factionlands.civilization_missing"));
		}
		StructureTemplate template = found.get();
		int sx = template.getSize().getX(), sy = template.getSize().getY(), sz = template.getSize().getZ();

		// huella de la plantilla ya rotada, relativa al origen
		int minX = Integer.MAX_VALUE, maxX = Integer.MIN_VALUE, minZ = Integer.MAX_VALUE, maxZ = Integer.MIN_VALUE;
		for (int[] corner : new int[][] {{0, 0}, {sx - 1, 0}, {0, sz - 1}, {sx - 1, sz - 1}}) {
			int[] p = rotate(corner[0], corner[1], rotation);
			minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]);
			minZ = Math.min(minZ, p[1]); maxZ = Math.max(maxZ, p[1]);
		}
		BlockPos origin = new BlockPos(ground.getX() - Math.floorDiv(minX + maxX, 2), ground.getY() - FLOOR,
				ground.getZ() - Math.floorDiv(minZ + maxZ, 2));
		int x0 = origin.getX() + minX, x1 = origin.getX() + maxX;
		int z0 = origin.getZ() + minZ, z1 = origin.getZ() + maxZ;
		int y0 = origin.getY(), y1 = origin.getY() + sy - 1 + CLEAR_EXTRA;

		if (y0 < level.getMinY() || y1 > level.getMaxY()) {
			return new Result(false, Component.translatable("message.factionlands.civilization_height"));
		}
		if (!level.hasChunksAt(new BlockPos(x0, y0, z0), new BlockPos(x1, y1, z1))) {
			return new Result(false, Component.translatable("message.factionlands.civilization_unloaded"));
		}

		BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
		BlockState air = Blocks.AIR.defaultBlockState();
		// 1) despejar árboles, colinas y vegetación encima de la calle
		for (int x = x0; x <= x1; x++) {
			for (int z = z0; z <= z1; z++) {
				for (int y = origin.getY() + FLOOR + 1; y <= y1; y++) {
					pos.set(x, y, z);
					if (!level.getBlockState(pos).isAir()) {
						level.setBlock(pos, air, Block.UPDATE_CLIENTS);
					}
				}
			}
		}
		// 2) colocar la plantilla (con sus habitantes)
		StructurePlaceSettings settings = new StructurePlaceSettings().setRotation(rotation).setIgnoreEntities(false);
		template.placeInWorld(level, origin, origin, settings, level.getRandom(), Block.UPDATE_CLIENTS);
		// 3) rellenar de tierra los huecos bajo la aldea hasta encontrar suelo firme
		BlockState dirt = Blocks.DIRT.defaultBlockState();
		for (int x = x0; x <= x1; x++) {
			for (int z = z0; z <= z1; z++) {
				for (int y = origin.getY() - 1; y >= Math.max(origin.getY() - SKIRT_DEPTH, level.getMinY()); y--) {
					pos.set(x, y, z);
					BlockState state = level.getBlockState(pos);
					if (state.isAir() || state.canBeReplaced() || !state.getFluidState().isEmpty()) {
						level.setBlock(pos, dirt, Block.UPDATE_CLIENTS);
					} else {
						break;
					}
				}
			}
		}
		return new Result(true, Component.translatable("message.factionlands.civilization_founded",
				Component.translatable("item.factionlands." + faction.id + "_civilization")));
	}

	private Civilizations() {}
}
