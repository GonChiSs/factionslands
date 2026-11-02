package com.factionlands;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;

/** Los ocho roles que se repiten en cada lámina, de izquierda a derecha y de arriba abajo. */
public enum Role {
	LEADER    ("leader",     1.50, 1.20, false, false),
	LUMBERJACK("lumberjack", 0.90, 0.60, false, false),
	MASON     ("mason",      0.90, 0.60, false, false),
	SMITH     ("smith",      1.00, 0.70, false, false),
	WARRIOR   ("warrior",    1.25, 1.50, false, false),
	ARCHER    ("archer",     0.80, 0.80, true,  false),
	SCOUT     ("scout",      0.85, 0.60, false, false),
	MYSTIC    ("mystic",     0.80, 0.30, false, true);

	public final String id;
	public final double healthMul, damageMul;
	public final boolean ranged, healer;

	Role(String id, double healthMul, double damageMul, boolean ranged, boolean healer) {
		this.id = id;
		this.healthMul = healthMul;
		this.damageMul = damageMul;
		this.ranged = ranged;
		this.healer = healer;
	}

	/** Objeto en la mano: los arcos, bastones y martillos de las láminas se aproximan con ítems vanilla. */
	public Item mainHand(Faction f) {
		return switch (this) {
			case LEADER -> f == Faction.TROLL ? Items.STONE_AXE : Items.GOLDEN_SWORD;
			case LUMBERJACK -> Items.IRON_AXE;
			case MASON -> Items.STONE_PICKAXE;
			case SMITH -> Items.IRON_PICKAXE;
			case WARRIOR -> f == Faction.TROLL ? Items.STONE_AXE : Items.IRON_SWORD;
			case ARCHER -> f == Faction.TROLL ? Items.AIR : Items.BOW;
			case SCOUT -> Items.SPYGLASS;
			case MYSTIC -> Items.BLAZE_ROD;
		};
	}

	public Item offHand() {
		return this == WARRIOR ? Items.SHIELD : Items.AIR;
	}
}
