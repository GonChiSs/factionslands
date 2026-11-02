package com.factionlands;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import net.fabricmc.loader.api.FabricLoader;

/** Configuración mínima en config/factionlands.json (se crea con valores por defecto al primer arranque). */
public final class Config {
	private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

	/** Los trols atacan a las demás facciones. */
	public boolean factionWars = true;
	/** Los trols atacan a los jugadores en modo supervivencia. */
	public boolean trollsHostileToPlayers = true;
	/** Distancia máxima (en bloques) a la que se alejan del punto donde aparecieron. */
	public int homeRadius = 28;

	private static Config instance = new Config();

	public static Config get() {
		return instance;
	}

	public static void load() {
		Path file = FabricLoader.getInstance().getConfigDir().resolve("factionlands.json");
		try {
			if (Files.exists(file)) {
				try (Reader reader = Files.newBufferedReader(file)) {
					Config loaded = GSON.fromJson(reader, Config.class);
					if (loaded != null) {
						instance = loaded;
					}
				}
			}
			try (Writer writer = Files.newBufferedWriter(file)) {
				GSON.toJson(instance, writer);
			}
		} catch (IOException | RuntimeException e) {
			FactionLands.LOGGER.warn("No se pudo leer/escribir {}; se usan los valores por defecto", file, e);
		}
	}

	private Config() {}
}
