package com.factionlands;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import net.minecraft.resources.Identifier;

import net.fabricmc.api.ModInitializer;

public class FactionLands implements ModInitializer {
	public static final String MOD_ID = "factionlands";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	public static Identifier id(String path) {
		return Identifier.fromNamespaceAndPath(MOD_ID, path);
	}

	@Override
	public void onInitialize() {
		Config.load();
		ModEntities.initialize();
		ModItems.initialize();
		ModCommands.initialize();
	}
}
