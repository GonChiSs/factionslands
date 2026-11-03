package com.factionlands.item;

import java.util.function.Consumer;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.item.context.UseOnContext;

import com.factionlands.Civilizations;
import com.factionlands.Faction;

/** Estandarte de civilización: clic derecho en el suelo y aparece la aldea completa de la facción. */
public class CivilizationItem extends Item {
	private final Faction faction;

	public CivilizationItem(Properties properties, Faction faction) {
		super(properties);
		this.faction = faction;
	}

	public Faction getFaction() {
		return faction;
	}

	@Override
	public InteractionResult useOn(UseOnContext context) {
		if (!(context.getLevel() instanceof ServerLevel level)) {
			return InteractionResult.SUCCESS;
		}
		BlockPos ground = context.getClickedPos();
		if (level.getBlockState(ground).canBeReplaced()) {
			ground = ground.below(); // se pulsó sobre hierba alta u otra planta
		}
		Civilizations.Result result = Civilizations.found(level, ground,
				Civilizations.rotationFor(context.getHorizontalDirection()), faction);
		Player player = context.getPlayer();
		if (player != null) {
			player.sendSystemMessage(result.message());
		}
		if (!result.ok()) {
			return InteractionResult.FAIL;
		}
		if (player != null && !player.isCreative()) {
			context.getItemInHand().consume(1, player);
		}
		return InteractionResult.SUCCESS_SERVER;
	}

	@Override
	public void appendHoverText(ItemStack stack, Item.TooltipContext context, TooltipDisplay display,
								Consumer<Component> lines, TooltipFlag flag) {
		lines.accept(Component.translatable("item.factionlands.civilization.tooltip").withStyle(ChatFormatting.GRAY));
		lines.accept(Component.translatable("item.factionlands.civilization.tooltip2").withStyle(ChatFormatting.DARK_GRAY));
	}
}
