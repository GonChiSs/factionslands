#!/usr/bin/env bash
# Vuelca las firmas reales de la API de Minecraft 26.3 que usa el mod (se ejecuta en CI tras el build).
set +e
echo "##### buscando jars de Minecraft"
MC=""
for j in $(find ~/.gradle -name '*.jar' 2>/dev/null); do
  if unzip -l "$j" 2>/dev/null | grep -q -E 'net/minecraft/(world/entity/EntityType|client/renderer/entity/HumanoidMobRenderer)\.class'; then
    echo "  $j"; MC="$MC:$j"
  fi
done
MC="${MC#:}"
for j in ${MC//:/ }; do unzip -p "$j" version.json 2>/dev/null | head -12 && break; done

jp() { echo; echo "===== $1 ${2:+(filtro: $2)}"; if [ -n "$2" ]; then javap -p -cp "$MC" "$1" 2>&1 | grep -E "$2"; else javap -p -cp "$MC" "$1" 2>&1; fi; }

jp net.minecraft.world.entity.EntityType 'ARROW|public .* create\(|Builder'
jp 'net.minecraft.world.entity.EntityType$Builder' 'of\(|sized|build\(|clientTracking'
jp net.minecraft.world.entity.projectile.arrow.Arrow 'Arrow\(|class|shoot|BaseDamage'
jp net.minecraft.world.entity.projectile.arrow.AbstractArrow 'AbstractArrow\(|pickup|BaseDamage|Pickup'
jp net.minecraft.world.entity.projectile.Projectile 'static|shoot|setOwner'
jp net.minecraft.world.entity.Mob 'setHomeTo|finalizeSpawn|setTarget|setPersistenceRequired|removeWhenFarAway|setItemSlot|setDropChance'
jp net.minecraft.world.entity.LivingEntity 'hurtServer|getHurtSound|getDeathSound|aiStep|heal\(|getMaxHealth'
jp net.minecraft.world.entity.player.Player 'sendSystemMessage|displayClientMessage|sendOverlay'
jp net.minecraft.world.entity.monster.RangedAttackMob
jp net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal 'NearestAttackableTargetGoal\(|Selector'
jp net.minecraft.world.entity.ai.goal.RangedAttackGoal 'RangedAttackGoal\('
jp net.minecraft.world.entity.ai.goal.MeleeAttackGoal 'MeleeAttackGoal\('
jp net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal 'MoveTowardsRestrictionGoal\('
jp net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal 'HurtByTargetGoal\('
jp net.minecraft.world.entity.ai.goal.LookAtPlayerGoal 'LookAtPlayerGoal\('
jp net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal 'WaterAvoidingRandomStrollGoal\('
jp net.minecraft.world.entity.ai.attributes.Attributes 'SCALE|MAX_HEALTH|ARMOR|FOLLOW_RANGE|KNOCKBACK'
jp net.minecraft.world.InteractionResult 'SUCCESS|PASS'
jp net.minecraft.world.item.Item\$Properties 'spawnEgg|setId'
jp net.minecraft.world.item.SpawnEggItem 'SpawnEggItem\('
jp net.minecraft.world.level.storage.ValueInput 'getInt|getIntOr'
jp net.minecraft.world.level.storage.ValueOutput 'putInt'
jp net.minecraft.sounds.SoundEvents 'SKELETON_SHOOT|IRON_GOLEM_HURT|IRON_GOLEM_DEATH|VILLAGER_HURT|VILLAGER_DEATH'
jp net.minecraft.world.entity.EntitySpawnReason 'TRIGGERED|STRUCTURE'
jp net.minecraft.client.renderer.entity.HumanoidMobRenderer
jp net.minecraft.client.renderer.entity.state.HumanoidRenderState 'class'
jp net.minecraft.client.renderer.entity.EntityRenderers 'register'
jp net.minecraft.client.model.geom.ModelLayers ' PLAYER'
jp net.minecraft.client.model.HumanoidModel 'HumanoidModel\('
