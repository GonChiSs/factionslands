package com.factionlands.entity;

import java.util.Optional;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RangedAttackGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.monster.RangedAttackMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.arrow.Arrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;

import com.factionlands.Config;
import com.factionlands.Faction;
import com.factionlands.Role;

/** Una sola clase para los 40 habitantes: el comportamiento depende de (facción, rol). */
public class FactionEntity extends PathfinderMob implements RangedAttackMob {
	private final Faction faction;
	private final Role role;
	private BlockPos home;

	public FactionEntity(EntityType<? extends FactionEntity> type, Level level, Faction faction, Role role) {
		super(type, level);
		this.faction = faction;
		this.role = role;
	}

	public Faction getFaction() {
		return faction;
	}

	public Role getRole() {
		return role;
	}

	public static AttributeSupplier.Builder createAttributes(Faction f, Role r) {
		return PathfinderMob.createMobAttributes()
				.add(Attributes.MAX_HEALTH, f.health * r.healthMul)
				.add(Attributes.ATTACK_DAMAGE, Math.max(1.0, f.damage * r.damageMul))
				.add(Attributes.MOVEMENT_SPEED, f.speed)
				.add(Attributes.KNOCKBACK_RESISTANCE, f.knockbackResistance)
				.add(Attributes.ARMOR, f.armor)
				.add(Attributes.FOLLOW_RANGE, 24.0)
				.add(Attributes.SCALE, f.scale); // escala hitbox y modelo a la vez
	}

	// ───────────────────────────── IA ─────────────────────────────

	@Override
	protected void registerGoals() {
		this.goalSelector.addGoal(0, new FloatGoal(this));
		if (role.ranged && role.mainHand(faction) != Items.AIR) {
			this.goalSelector.addGoal(2, new RangedAttackGoal(this, 1.0, 25, 16.0F));
		} else {
			this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.1, true));
		}
		this.goalSelector.addGoal(5, new MoveTowardsRestrictionGoal(this, 0.8));
		this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.7));
		this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 8.0F));
		this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));

		this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
		// 1.21.2+: el selector recibe también el ServerLevel
		this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 10, true, false,
				(target, level) -> wantsToAttack(target)));
	}

	private boolean wantsToAttack(LivingEntity target) {
		if (target instanceof FactionEntity other) {
			return Config.get().factionWars && faction.isHostileTo(other.faction);
		}
		if (target instanceof Player player) {
			return faction == Faction.TROLL && Config.get().trollsHostileToPlayers
					&& !player.isCreative() && !player.isSpectator();
		}
		return faction != Faction.TROLL && target instanceof Enemy;
	}

	private boolean isSameFaction(Entity other) {
		return other instanceof FactionEntity f && f.faction == faction;
	}

	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float damage) {
		boolean hurt = super.hurtServer(level, source, damage);
		if (hurt && source.getEntity() instanceof LivingEntity attacker && !isSameFaction(attacker)
				&& !(attacker instanceof Player p && (p.isCreative() || p.isSpectator()))) {
			// los de su misma facción acuden a defenderlo (los místicos se quedan curando)
			for (FactionEntity ally : level.getEntitiesOfClass(FactionEntity.class, getBoundingBox().inflate(16.0),
					e -> e != this && e.faction == faction && e.role != Role.MYSTIC && e.getTarget() == null)) {
				ally.setTarget(attacker);
			}
		}
		return hurt;
	}

	@Override
	public void performRangedAttack(LivingEntity target, float power) {
		if (!(level() instanceof ServerLevel server)) {
			return;
		}
		ItemStack weapon = getMainHandItem();
		// 26.x: el constructor coloca la flecha en los ojos del tirador; no existe EntityType.ARROW
		Arrow arrow = new Arrow(server, this, new ItemStack(Items.ARROW), weapon);
		double dx = target.getX() - getX();
		double dy = target.getY(0.3333333333333333) - arrow.getY();
		double dz = target.getZ() - getZ();
		double dist = Math.sqrt(dx * dx + dz * dz);
		Projectile.spawnProjectileUsingShoot(arrow, server, weapon, dx, dy + dist * 0.2, dz, 1.6F, rangedAttackUncertainty(server));
		playSound(SoundEvents.SKELETON_SHOOT, 1.0F, 1.0F / (getRandom().nextFloat() * 0.4F + 0.8F));
	}

	@Override
	public void aiStep() {
		super.aiStep();
		if (role.healer && tickCount % 80 == 0 && level() instanceof ServerLevel server) {
			for (FactionEntity ally : server.getEntitiesOfClass(FactionEntity.class, getBoundingBox().inflate(8.0),
					e -> e.isAlive() && e.faction == faction && e.getHealth() < e.getMaxHealth())) {
				healWithParticles(server, ally, 4.0F);
			}
			if (faction != Faction.TROLL) {
				for (Player p : server.getEntitiesOfClass(Player.class, getBoundingBox().inflate(6.0),
						e -> e.isAlive() && e.getHealth() < e.getMaxHealth())) {
					healWithParticles(server, p, 2.0F);
				}
			}
		}
	}

	private static void healWithParticles(ServerLevel server, LivingEntity target, float amount) {
		target.heal(amount);
		server.sendParticles(ParticleTypes.HEART, target.getX(), target.getEyeY(), target.getZ(), 3, 0.3, 0.3, 0.3, 0.0);
	}

	// ───────────────────────────── aparición y persistencia ─────────────────────────────

	@Override
	public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, EntitySpawnReason reason,
										SpawnGroupData groupData) {
		SpawnGroupData data = super.finalizeSpawn(level, difficulty, reason, groupData);
		setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(role.mainHand(faction)));
		setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(role.offHand()));
		setPersistenceRequired();
		home = blockPosition();
		setHomeTo(home, Config.get().homeRadius);
		return data;
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput out) {
		super.addAdditionalSaveData(out);
		if (home != null) {
			out.putInt("HomeX", home.getX());
			out.putInt("HomeY", home.getY());
			out.putInt("HomeZ", home.getZ());
		}
	}

	@Override
	protected void readAdditionalSaveData(ValueInput in) {
		super.readAdditionalSaveData(in);
		Optional<Integer> x = in.getInt("HomeX");
		if (x.isPresent()) {
			home = new BlockPos(x.get(), in.getInt("HomeY").orElse(0), in.getInt("HomeZ").orElse(0));
			setHomeTo(home, Config.get().homeRadius);
		}
	}

	// ───────────────────────────── interacción y sonidos ─────────────────────────────

	@Override
	protected InteractionResult mobInteract(Player player, InteractionHand hand) {
		if (hand != InteractionHand.MAIN_HAND) {
			return InteractionResult.PASS;
		}
		if (level().isClientSide()) {
			return InteractionResult.SUCCESS;
		}
		player.sendSystemMessage(Component.translatable("dialog.factionlands.chat",
				getDisplayName(), Component.translatable("dialog.factionlands." + role.id)));
		return InteractionResult.SUCCESS_SERVER;
	}

	@Override
	protected SoundEvent getHurtSound(DamageSource source) {
		return faction == Faction.TROLL ? SoundEvents.IRON_GOLEM_HURT : SoundEvents.VILLAGER_HURT;
	}

	@Override
	protected SoundEvent getDeathSound() {
		return faction == Faction.TROLL ? SoundEvents.IRON_GOLEM_DEATH : SoundEvents.VILLAGER_DEATH;
	}
}
