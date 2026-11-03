package com.factionlands.ai;

import java.util.EnumSet;
import java.util.Set;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

import com.factionlands.FactionLands;
import com.factionlands.Role;
import com.factionlands.entity.FactionEntity;

/**
 * Trabajo de los oficios: de día, el leñador, el albañil y el herrero van a su puesto de trabajo (mesa, barril,
 * yunque, forja...) dentro de su zona, trabajan un rato golpeando con el brazo y descansan. No modifican el mundo.
 */
public class WorkGoal extends Goal {
	private static final int RADIUS = 14, HEIGHT = 4, WORK_TICKS = 220;
	private static final boolean DEBUG = Boolean.getBoolean("factionlands.debug");

	private final FactionEntity mob;
	private final double speed;
	private BlockPos station;
	private int worked, repath, cooldown;

	public WorkGoal(FactionEntity mob, double speed) {
		this.mob = mob;
		this.speed = speed;
		setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
	}

	public static boolean hasJob(Role role) {
		return role == Role.LUMBERJACK || role == Role.MASON || role == Role.SMITH;
	}

	private Set<Block> stations() {
		return switch (mob.getRole()) {
			case LUMBERJACK -> Set.of(Blocks.CRAFTING_TABLE, Blocks.BARREL);
			case MASON -> Set.of(Blocks.STONECUTTER, Blocks.GRINDSTONE, Blocks.FURNACE);
			default -> Set.of(Blocks.ANVIL, Blocks.CHIPPED_ANVIL, Blocks.DAMAGED_ANVIL, Blocks.BLAST_FURNACE,
					Blocks.SMITHING_TABLE, Blocks.GRINDSTONE);
		};
	}

	private boolean isDay(ServerLevel level) {
		return level.getDayTime() % 24000L < 12000L;
	}

	@Override
	public boolean canUse() {
		if (!(mob.level() instanceof ServerLevel level) || mob.getTarget() != null || !isDay(level)) {
			return false;
		}
		if (cooldown > 0) {
			cooldown--;
			return false;
		}
		if (mob.getRandom().nextInt(20) != 0) {
			return false;
		}
		station = findStation(level);
		return station != null;
	}

	private BlockPos findStation(ServerLevel level) {
		Set<Block> wanted = stations();
		BlockPos origin = mob.blockPosition();
		BlockPos best = null;
		double bestDist = Double.MAX_VALUE;
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
		for (int dx = -RADIUS; dx <= RADIUS; dx++) {
			for (int dz = -RADIUS; dz <= RADIUS; dz++) {
				for (int dy = -HEIGHT; dy <= HEIGHT; dy++) {
					p.set(origin.getX() + dx, origin.getY() + dy, origin.getZ() + dz);
					if (wanted.contains(level.getBlockState(p).getBlock())) {
						double d = p.distSqr(origin);
						if (d < bestDist) {
							bestDist = d;
							best = p.immutable();
						}
					}
				}
			}
		}
		return best;
	}

	@Override
	public boolean canContinueToUse() {
		return station != null && worked < WORK_TICKS && mob.getTarget() == null
				&& mob.level() instanceof ServerLevel level && isDay(level)
				&& stations().contains(level.getBlockState(station).getBlock());
	}

	@Override
	public void start() {
		worked = 0;
		repath = 0;
		if (DEBUG) {
			FactionLands.LOGGER.info("WORK start {} -> {}", mob.getType().toShortString(), station);
		}
	}

	@Override
	public void tick() {
		double dist = mob.distanceToSqr(station.getX() + 0.5, station.getY() + 0.5, station.getZ() + 0.5);
		mob.getLookControl().setLookAt(station.getX() + 0.5, station.getY() + 0.5, station.getZ() + 0.5);
		if (dist > 6.25) { // a más de 2,5 bloques: acercarse
			if (--repath <= 0) {
				repath = 10;
				mob.getNavigation().moveTo(station.getX() + 0.5, station.getY(), station.getZ() + 0.5, speed);
			}
			return;
		}
		mob.getNavigation().stop();
		worked++;
		if (worked % 18 == 0) {
			mob.swing(InteractionHand.MAIN_HAND);
			if (mob.level() instanceof ServerLevel level) {
				BlockState state = level.getBlockState(station);
				SoundEvent hit = state.getSoundType().getHitSound();
				mob.playSound(hit, 0.6F, 0.9F + mob.getRandom().nextFloat() * 0.2F);
			}
		}
	}

	@Override
	public void stop() {
		if (DEBUG && worked >= WORK_TICKS) {
			FactionLands.LOGGER.info("WORK done {}", mob.getType().toShortString());
		}
		station = null;
		mob.getNavigation().stop();
		cooldown = 200 + mob.getRandom().nextInt(400); // descanso antes del siguiente turno
	}
}
