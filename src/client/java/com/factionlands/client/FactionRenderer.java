package com.factionlands.client;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.resources.Identifier;

import com.factionlands.FactionLands;
import com.factionlands.entity.FactionEntity;
import com.factionlands.ModEntities;

/**
 * Modelo humanoide de 64x64 con la skin muestreada de la lámina de referencia.
 * Hay una instancia por habitante, así que la textura es fija; el tamaño lo da el atributo SCALE.
 */
public class FactionRenderer extends HumanoidMobRenderer<FactionEntity, HumanoidRenderState, HumanoidModel<HumanoidRenderState>> {
	private final Identifier texture;

	public FactionRenderer(EntityRendererProvider.Context context, ModEntities.Def def) {
		super(context, new HumanoidModel<>(context.bakeLayer(ModelLayers.PLAYER)), 0.5F);
		this.texture = FactionLands.id("textures/entity/" + def.faction().id + "/" + def.role().id + ".png");
	}

	@Override
	public HumanoidRenderState createRenderState() {
		return new HumanoidRenderState();
	}

	@Override
	public Identifier getTextureLocation(HumanoidRenderState state) {
		return texture;
	}
}
