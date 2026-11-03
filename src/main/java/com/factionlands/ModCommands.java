package com.factionlands;

import com.mojang.brigadier.builder.LiteralArgumentBuilder;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;

import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;

/** /factionlands civilization <facción>: funda la aldea en tu posición (mismo código que el objeto del menú creativo). */
public final class ModCommands {
	public static void initialize() {
		CommandRegistrationCallback.EVENT.register((dispatcher, buildContext, selection) -> {
			LiteralArgumentBuilder<CommandSourceStack> civilization = Commands.literal("civilization");
			for (Faction faction : Faction.values()) {
				civilization.then(Commands.literal(faction.id).executes(ctx -> found(ctx.getSource(), faction)));
			}
			dispatcher.register(Commands.literal("factionlands")
					.requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
					.then(civilization));
		});
	}

	private static int found(CommandSourceStack source, Faction faction) {
		BlockPos ground = BlockPos.containing(source.getPosition()).below();
		Direction facing = Direction.fromYRot(source.getRotation().y);
		Civilizations.Result result = Civilizations.found(source.getLevel(), ground, Civilizations.rotationFor(facing), faction);
		if (result.ok()) {
			source.sendSuccess(result::message, true);
			return 1;
		}
		source.sendFailure(result.message());
		return 0;
	}

	private ModCommands() {}
}
