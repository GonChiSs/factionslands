package com.factionlands;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SpawnEggItem;

import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;

import com.factionlands.item.CivilizationItem;

/**
 * Huevos de aparición (uno por habitante), estandartes de civilización (uno por facción) y la pestaña creativa
 * «Factionlands»: una fila por facción = estandarte + los 8 roles. Los colores de los huevos van en assets/.../items/*.json.
 */
public final class ModItems {
	/** En el orden de ModEntities.DEFS: facción (exterior) x rol (interior). */
	public static final List<Item> EGGS = new ArrayList<>();
	public static final Map<Faction, Item> CIVILIZATIONS = new EnumMap<>(Faction.class);

	public static final ResourceKey<CreativeModeTab> TAB_KEY =
			ResourceKey.create(Registries.CREATIVE_MODE_TAB, FactionLands.id("main"));

	public static void initialize() {
		for (ModEntities.Def def : ModEntities.DEFS) {
			ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, FactionLands.id(def.path() + "_spawn_egg"));
			Item egg = Registry.register(BuiltInRegistries.ITEM, key,
					new SpawnEggItem(new Item.Properties().setId(key).spawnEgg(def.type())));
			EGGS.add(egg);
		}
		for (Faction faction : Faction.values()) {
			ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, FactionLands.id(faction.id + "_civilization"));
			CIVILIZATIONS.put(faction, Registry.register(BuiltInRegistries.ITEM, key,
					new CivilizationItem(new Item.Properties().setId(key).stacksTo(1).rarity(Rarity.EPIC), faction)));
		}

		CreativeModeTab tab = FabricCreativeModeTab.builder()
				.title(Component.translatable("itemGroup.factionlands.main"))
				.icon(() -> new ItemStack(CIVILIZATIONS.get(Faction.HUMAN)))
				.displayItems((params, output) -> {
					int roles = Role.values().length;
					for (Faction faction : Faction.values()) {
						output.accept(CIVILIZATIONS.get(faction));
						for (Role role : Role.values()) {
							output.accept(EGGS.get(faction.ordinal() * roles + role.ordinal()));
						}
					}
				})
				.build();
		Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, TAB_KEY, tab);
	}

	private ModItems() {}
}
