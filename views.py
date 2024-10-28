# -*- coding: utf-8 -*-
import re

example = '''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- 楼栋 Form View -->
    <record id="view_building_form" model="ir.ui.view">
        <field name="name">building_form</field>
        <field name="model">building</field>
        <field name="arch" type="xml">
            <form string="楼栋">
                <sheet>
                    <group>
                        <field name="name"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- 楼栋 Tree View -->
    <record id="view_building_tree" model="ir.ui.view">
        <field name="name">building_tree</field>
        <field name="model">building</field>
        <field name="arch" type="xml">
            <tree string="楼栋">
                <field name="name" string="楼栋号"/>
            </tree>
        </field>
    </record>

    <!-- 楼栋 Search View -->
    <record id="view_building_search" model="ir.ui.view">
        <field name="name">building_search</field>
        <field name="model">building</field>
        <field name="arch" type="xml">
            <search string="楼栋">
                <field name="name" string="楼栋号"/>
            </search>
        </field>
    </record>

    <!-- 楼栋 Action -->
    <record id="action_building" model="ir.actions.act_window">
        <field name="name">楼栋信息</field>
        <field name="res_model">building</field>
        <field name="view_mode">tree,form</field>
        <field name="help" type="html">
            <p class="oe_view_nocontent_create">
                创建第一个楼栋信息
            </p>
        </field>
    </record>

    <!-- 楼栋 Menuitem -->
    <menuitem id="menu_building_root" name="楼栋" />
    <menuitem id="menu_building" name="楼栋信息" parent="menu_building_root" action="action_building" sequence="10"/>
</odoo>
'''



def generate_view(model_name, verbose_name, model_str,example_str=example):
    example_str = example_str.replace('<field name="model">building</field>',
                                      '<field name="model">{}</field>'.format(model_name))
    example_str = example_str.replace('<field name="res_model">building</field>',
                                      '<field name="res_model">{}</field>'.format(model_name))

    class_name = model_name.replace(".", "_")
    example_str = example_str.replace('building', class_name)
    example_str = example_str.replace('楼栋', verbose_name)

    # 定义待匹配的模式
    pattern = r'([a-z_]+)(\s).*?(?=\=).*?fields'

    # 使用正则表达式进行匹配
    matches = re.finditer(pattern, model_str)

    # 提取匹配到的字段名，并将 Unicode 编码转换为普通字符
    field_names = [match.group(1) for match in matches]

    result = ["\n\n"]
    # 输出结果
    for i in field_names:
        string = '<field name="%s"/>' % i
        result.append(string)

    return example_str + "\n".join(result)


if __name__=="__main__":
    model_name = "media.video"

    verbose_name = "视频"
    generate_view(model_name, verbose_name)