package com.factionlands.client;

import net.minecraft.client.renderer.entity.EntityRenderers;

import net.fabricmc.api.ClientModInitializer;

import com.factionlands.ModEntities;

public class FactionLandsClient implements ClientModInitializer {
	@Override
	public void onInitializeClient() {
		for (ModEntities.Def def : ModEntities.DEFS) {
			EntityRenderers.register(def.type(), context -> new FactionRenderer(context, def));
		}
	}
}
