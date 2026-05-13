from . import models


def post_init_hook(env):
    view = env.ref("motel_booking.view_motel_booking_form", raise_if_not_found=False)
    if not view:
        return

    existing = env.ref("motel_payment.view_motel_booking_form_inherit_payment", raise_if_not_found=False)
    if existing:
        return

    arch = """
<data>
    <xpath expr="//group/group/field[@name='deposit_amount']" position="after">
        <field name="paid_amount" readonly="1"/>
        <field name="remaining_balance" readonly="1"/>
    </xpath>
    <xpath expr="//notebook" position="inside">
        <page string="Payments">
            <field name="payment_ids" readonly="1">
                <tree>
                    <field name="payment_time"/>
                    <field name="amount"/>
                    <field name="payment_method"/>
                    <field name="state"/>
                    <field name="reference"/>
                </tree>
            </field>
        </page>
    </xpath>
</data>
    """.strip()

    inherited_view = env["ir.ui.view"].create(
        {
            "name": "motel.booking.form.inherit.payment",
            "type": "form",
            "model": "motel.booking",
            "inherit_id": view.id,
            "arch": arch,
        }
    )
    env["ir.model.data"].create(
        {
            "name": "view_motel_booking_form_inherit_payment",
            "module": "motel_payment",
            "model": "ir.ui.view",
            "res_id": inherited_view.id,
            "noupdate": True,
        }
    )
