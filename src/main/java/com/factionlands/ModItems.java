package com.factionlands;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;

import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;

/** Un huevo de aparición por habitante, en la pestaña vanilla de huevos. Los colores van en assets/.../items/*.json. */
public final class ModItems {
	public static final List<Item> EGGS = new ArrayList<>();

	public static void initialize() {
		for (ModEntities.Def def : ModEntities.DEFS) {
			ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, FactionLands.id(def.path() + "_spawn_egg"));
			Item egg = Registry.register(BuiltInRegistries.ITEM, key,
					new SpawnEggItem(new Item.Properties().setId(key).spawnEgg(def.type())));
			EGGS.add(egg);
		}
		CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.SPAWN_EGGS)
				.register(tab -> EGGS.forEach(egg -> tab.accept(egg)));
	}

	private ModItems() {}
}
