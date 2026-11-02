package com.factionlands;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;

import com.factionlands.entity.FactionEntity;

/** Registra los 40 tipos de entidad (5 facciones x 8 roles). */
public final class ModEntities {
	/** Un habitante concreto: raza + rol + su tipo de entidad registrado. */
	public record Def(Faction faction, Role role, String path, EntityType<FactionEntity> type) {}

	public static final List<Def> DEFS = new ArrayList<>();

	public static void initialize() {
		for (Faction faction : Faction.values()) {
			for (Role role : Role.values()) {
				String path = faction.id + "_" + role.id;
				ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, FactionLands.id(path));
				EntityType<FactionEntity> type = Registry.register(BuiltInRegistries.ENTITY_TYPE, key,
						EntityType.Builder.<FactionEntity>of((t, level) -> new FactionEntity(t, level, faction, role), MobCategory.MISC)
								.sized(0.6f, 1.95f)
								.clientTrackingRange(10)
								.build(key));
				FabricDefaultAttributeRegistry.register(type, FactionEntity.createAttributes(faction, role));
				DEFS.add(new Def(faction, role, path, type));
			}
		}
	}

	private ModEntities() {}
}
