package com.factionlands;

/** Las cinco facciones. La escala y los atributos salen de las proporciones de las láminas de referencia. */
public enum Faction {
	//     id        escala vida  daño  veloc. knockRes armadura
	TROLL ("troll",  1.30f, 40.0, 7.0, 0.24, 0.60, 2.0),
	KNIGHT("knight", 1.05f, 30.0, 5.0, 0.25, 0.15, 6.0),
	ELF   ("elf",    0.95f, 20.0, 3.0, 0.32, 0.00, 0.0),
	DWARF ("dwarf",  0.85f, 28.0, 5.0, 0.23, 0.30, 4.0),
	HUMAN ("human",  1.00f, 24.0, 3.5, 0.25, 0.00, 1.0);

	public final String id;
	public final float scale;
	public final double health, damage, speed, knockbackResistance, armor;

	Faction(String id, float scale, double health, double damage, double speed, double knockbackResistance, double armor) {
		this.id = id;
		this.scale = scale;
		this.health = health;
		this.damage = damage;
		this.speed = speed;
		this.knockbackResistance = knockbackResistance;
		this.armor = armor;
	}

	/** Los trols combaten a todas las demás facciones; el resto convive en paz. */
	public boolean isHostileTo(Faction other) {
		return other != this && this == TROLL;
	}
}
