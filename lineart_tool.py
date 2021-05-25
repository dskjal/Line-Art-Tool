# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
import bpy
import bmesh
from bpy.props import *

bl_info = {
    "name" : "Line Art Tool",
    "author" : "dskjal",
    "version" : (2, 0),
    "blender" : (2, 93, 0),
    "location" : "View3D > Sidebar > Tool > Line Art Tool",
    "description" : "",
    "warning" : "",
    "wiki_url" : "https://github.com/dskjal/Line-Art-Tool",
    "tracker_url" : "",
    "category" : "Mesh"
}

default_filter_source = 'lineart_'
opacity_vertex_group_suffix = '_opacity'
thickness_vertex_group_suffix = '_thickness'
opacity_modifier_name = 'lt_opacity'
thickness_modifier_name = 'lt_thickness'
tint_modifier_name = 'lt_tint'
base_color_name = 'lt_base_color'

def get_filter_source():
    gp = get_lineart_gpencil(is_create=False)
    if gp is None:
        return default_filter_source
    return gp.grease_pencil_modifiers[bpy.context.scene.lineart_tool_props.lineart_modifier].source_vertex_group

def create_lineart_grease_pencil():
    ob = bpy.context.active_object
    old_mode = 'OBJECT' if ob is None else ob.mode
    if ob is not None:
        bpy.ops.object.mode_set(mode='OBJECT')

    gp_data = bpy.data.grease_pencils.new('Line Art')
    material = bpy.data.materials.new(base_color_name)
    bpy.data.materials.create_gpencil_data(material)
    gp_data.materials.append(material)
    layer = gp_data.layers.new('GP_Layer')
    layer.frames.new(bpy.context.scene.frame_current)
    
    gp = bpy.data.objects.new('Line Art', gp_data)
    bpy.context.scene.collection.objects.link(gp)

    gp.show_in_front = True
    la = gp.grease_pencil_modifiers.new(name='Line Art', type='GP_LINEART')
    la.source_type = 'SCENE'
    la.target_layer = layer.info
    la.target_material = material
    filter_source = get_filter_source()
    la.source_vertex_group = filter_source

    # thickness modifier
    thick = gp.grease_pencil_modifiers.new(name=thickness_modifier_name, type='GP_THICK')
    thick.normalize_thickness = True
    thick_vg_name = filter_source + thickness_vertex_group_suffix
    gp.vertex_groups.new(name=thick_vg_name)
    thick.vertex_group = thick_vg_name

    # opacity modifier
    opacity = gp.grease_pencil_modifiers.new(name=opacity_modifier_name, type='GP_OPACITY')
    opacity.factor = 0
    opacity_vg_name = filter_source + opacity_vertex_group_suffix
    gp.vertex_groups.new(name=opacity_vg_name)
    opacity.vertex_group = opacity_vg_name

    bpy.context.scene.lineart_tool_props.gp_object = gp
    bpy.context.scene.lineart_tool_props.lineart_modifier = 'Line Art'

    if ob is not None:
        bpy.ops.object.mode_set(mode=old_mode)

def get_lineart_gpencil(is_create=True):
    gp = bpy.context.scene.lineart_tool_props.gp_object
    la_name = bpy.context.scene.lineart_tool_props.lineart_modifier
    if gp != None:
        if gp.grease_pencil_modifiers.find(la_name) != -1 and gp.grease_pencil_modifiers[la_name].type == 'GP_LINEART':
            return gp

    if is_create:
        return create_lineart_grease_pencil()
    
    return None

def create_lineart_vertex_group(ob, filter_source):
    vgs = [vg.name for vg in ob.vertex_groups if vg.name.startswith(filter_source)]
    gp = get_lineart_gpencil()
    for vg in vgs:
        if gp.vertex_groups.find(vg) == -1:
            gp.vertex_groups.new(name=vg)

def get_vertex_group(ob, vertex_group_name):
    id = ob.vertex_groups.find(vertex_group_name)
    if id == -1:
        return ob.vertex_groups.new(name=vertex_group_name)
    else:
        return ob.vertex_groups[id]
    
# modifier={'GP_OPACITY', 'GP_THICK', 'GP_TINT'}
def get_gp_modifiers(modifier):
    gp = get_lineart_gpencil()
    return [m for m in gp.grease_pencil_modifiers if m.type == modifier]

def edit_vertex_group(modifier, type, weight=1):
    ob = bpy.context.active_object
    bpy.ops.object.mode_set(mode='OBJECT')

    selected_verts = [v.index for v in ob.data.vertices if v.select]
    if not selected_verts: # if selected_verts is empty
        bpy.ops.object.mode_set(mode='EDIT')
        return
    
    vg_name = modifier.vertex_group
    if vg_name == None:
        raise Exception('modifier ' + modifier.name + ' has no vertex_group.')
    
    vg = get_vertex_group(ob, vg_name)
    if type == 'ADD':
        vg.add(selected_verts, weight, 'REPLACE')
    elif type == 'REMOVE':
        vg.remove(selected_verts)
    else:
        raise Exception('edit_vertex_group(): wrong type')

    bpy.ops.object.mode_set(mode='EDIT')

class DSKJAL_OT_LINEART_TOOL_AUTO_SETUP(bpy.types.Operator):
    bl_idname = "dskjal.linearttoolautosetup"
    bl_label = "Setup Line Art"
  
    def execute(self, context):
        create_lineart_grease_pencil()
        return {'FINISHED'}

class DSKJAL_OT_LINEART_TOOL_FROM_ACTIVE_CAMERA_AND_LOCK(bpy.types.Operator):
    bl_idname = "dskjal.linearttoolfromactivecameraandlock"
    bl_label = "From Active Camera And Lock"
  
    def execute(self, context):
        camera = context.scene.camera
        old_active = context.active_object
        old_mode = 'OBJECT' if old_active is None else old_active.mode

        if camera is None:
            if old_active and old_active.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.camera_add()
            camera = context.scene.camera

        bpy.ops.view3d.view_camera()

        areas = [area for area in context.screen.areas if area.type == 'VIEW_3D']
        for area in areas:
            if hasattr(area.spaces[0], 'lock_camera'):
                area.spaces[0].lock_camera = True

        context.view_layer.objects.active = old_active
        bpy.ops.object.mode_set(mode=old_mode)
        return {'FINISHED'}

class DSKJAL_OT_LINEART_TOOL_FREE_CAMERA(bpy.types.Operator):
    bl_idname = "dskjal.linearttoolfreecamera"
    bl_label = "Free Camera"
  
    def execute(self, context):
        camera = context.scene.camera
        if camera is None:
            return {'FINISHED'}

        areas = [area for area in context.screen.areas if area.type == 'VIEW_3D']
        for area in areas:
            if hasattr(area.spaces[0], 'lock_camera'):
                area.spaces[0].lock_camera = False

        return {'FINISHED'}

class DSKJAL_OT_LINEART_TOOL_ADD_MODIFIER(bpy.types.Operator):
    bl_idname = "dskjal.linearttooladdmodifier"
    bl_label = "Add color"
    modifier_name : bpy.props.StringProperty()
    modifier_type : bpy.props.StringProperty() # {'GP_TINT', 'GP_THICK', 'GP_OPACITY'}
    
    def execute(self, context):
        gp = get_lineart_gpencil()
        m = gp.grease_pencil_modifiers.new(name=self.modifier_name, type=self.modifier_type)
        if self.modifier_type == 'GP_THICK':
            m.normalize_thickness = True
        filter_source = get_filter_source()
        vg_name = filter_source + m.name
        gp.vertex_groups.new(name=vg_name)
        m.vertex_group = vg_name
        ob = context.active_object
        if ob.vertex_groups.find(m.name) == -1:
            ob.vertex_groups.new(name=vg_name)
            create_lineart_vertex_group(ob, filter_source)
        else:
            # clear vertex group
            ob.vertex_groups.remove(ob.vertex_groups[m.name])
            ob.vertex_groups.new(name=vg_name)
            
        return {'FINISHED'}

# type = {'ADD', 'REMOVE', 'DELETE'}
# remove modifier if type == 'DELETE' 
class DSKJAL_OT_LINEART_TOOL_EDIT_MODIFIER(bpy.types.Operator):
    bl_idname = 'dskjal.linearttooleditmodifier'
    bl_label = 'Tint'
    modifier_name : bpy.props.StringProperty()
    type : bpy.props.StringProperty()
    def execute(self, context):
        gp = get_lineart_gpencil()
        m = gp.grease_pencil_modifiers[self.modifier_name]
        if self.type == 'DELETE':
            gp.grease_pencil_modifiers.remove(m)
        else:
            edit_vertex_group(modifier=m, type=self.type, weight=1)
        return {'FINISHED'}

class DSKJAL_PT_LINEART_TOOL_UI(bpy.types.Panel):
    bl_label = "Line Art Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    #@classmethod
    #def poll(self, context):
    #    return context.active_object and context.active_object.type in ('MESH', 'OBJECT')

    def draw(self, context):
        my_props = context.scene.lineart_tool_props
        self.layout.use_property_split = True
        col = self.layout.column(align=True)
        col.operator('dskjal.linearttoolautosetup', text='Add Line Art Grease Pencil')
        col.separator(factor=3)
        # camera
        col.label(text='Camera')
        row = col.row(align=True)
        row.operator('dskjal.linearttoolfromactivecameraandlock', text='Lock')
        row.operator('dskjal.linearttoolfreecamera', text='Free')
        col.separator()

        # Line Art
        if my_props.gp_object != None and my_props.gp_object.grease_pencil_modifiers.find(my_props.lineart_modifier) != -1:
            lineart_modifier = my_props.gp_object.grease_pencil_modifiers[my_props.lineart_modifier]
            # visibility icon
            row = col.row(align=True)
            row.use_property_split = False
            row.prop(lineart_modifier, 'show_in_editmode', text='')
            row.prop(lineart_modifier, 'show_viewport', text='')
            row.prop(lineart_modifier, 'show_render', text='')
            row.separator()
            row.label(text='Line Art')
        else:
            col.label(text='Line Art')

        grease_pencil = None
        line_art_modifier = None
        col.prop_search(my_props, 'gp_object', bpy.data, 'objects', text='GP Object')
        grease_pencil = my_props.gp_object
        if grease_pencil == None:
            return
            
        col.prop_search(my_props, 'lineart_modifier', grease_pencil, 'grease_pencil_modifiers', text='Line Art Modifier')
        # error check
        if grease_pencil.grease_pencil_modifiers.find(my_props.lineart_modifier) == -1:
            return
        if grease_pencil.grease_pencil_modifiers[my_props.lineart_modifier].type != 'GP_LINEART':
            return

        line_art_modifier = grease_pencil.grease_pencil_modifiers[my_props.lineart_modifier]
        col.separator()
        col.prop(line_art_modifier, 'source_type')
        if line_art_modifier.source_type == 'COLLECTION':
            col.prop(line_art_modifier, 'source_collection')
        elif line_art_modifier.source_type == 'OBJECT':
            col.prop(line_art_modifier, 'source_object')
            
        col.separator()
        #col.prop(line_art_modifier, 'source_vertex_group', text="Filter Source")

        # Edge type
        col.separator()
        col.label(text='Edge Types')
        row = col.row(align=True)
        row.use_property_split = False
        row.prop(line_art_modifier, 'use_contour', text='Contour', toggle=1)
        row.prop(line_art_modifier, 'use_material', text='Material Boundaries', toggle=1)
        row = col.row(align=True)
        row.use_property_split = False

        row.prop(line_art_modifier, 'use_intersection', text='Intersections', toggle=1)

        col.separator()
        col.use_property_split = False
        col.prop(line_art_modifier, 'use_edge_mark', text='Edge Marks', toggle=1)
        ob = context.active_object
        is_edit_mode = ob and ob.type in ('MESH', 'OBJECT') and context.active_object.mode == 'EDIT'
        if is_edit_mode:
            row = col.row(align=True)
            row.use_property_split = False
            ot = row.operator('mesh.mark_freestyle_edge', text="Mark")
            ot = row.operator('mesh.mark_freestyle_edge', text='Clear')
            ot.clear = True

        col.separator()
        col.use_property_split = False
        col.prop(line_art_modifier, 'use_crease', text='Crease', toggle=1)
        col.prop(line_art_modifier, 'crease_threshold', text='', slider=True)

        col.separator()

        col.use_property_split = True

        def print_modifier(modifier, modifier_name):
            modifiers = get_gp_modifiers(modifier=modifier)
            for m in modifiers:
                row = col.row(align=True)
                row.use_property_split = False
                ot = row.operator('dskjal.linearttooleditmodifier', icon='CANCEL', text='')
                ot.modifier_name = m.name
                ot.type = 'DELETE'
                row.prop(m, 'name', text='')
                if modifier == 'GP_OPACITY':
                    row.prop(m, 'factor', text='')
                elif modifier == 'GP_THICK':
                    row.prop(m, 'thickness', text='')

                if is_edit_mode:
                    row = col.row(align=True)
                    ot = row.operator('dskjal.linearttooleditmodifier', text='Assign')
                    ot.modifier_name = m.name
                    ot.type = 'ADD'
                    ot = row.operator('dskjal.linearttooleditmodifier', text='Remove')
                    ot.modifier_name = m.name
                    ot.type = 'REMOVE'
                    col.separator(factor=2)
                row = col.row(align=True)
                col.separator()

            if is_edit_mode:
                col.separator()
                ot = col.operator('dskjal.linearttooladdmodifier', text="Add Opacity")                
                ot.modifier_type = modifier
                ot.modifier_name = modifier_name

        # opacity
        col.separator()
        col.label(text='Opacity')
        # base
        col.prop(line_art_modifier, 'opacity', text='Base Opacity')
        col.separator()
        print_modifier(modifier='GP_OPACITY', modifier_name=opacity_modifier_name)

        # thickness
        col.separator()
        col.label(text='Thickness')
        # base
        col.prop(line_art_modifier, 'thickness', text='Base Thickness')
        col.separator()
        print_modifier(modifier='GP_THICK', modifier_name=thickness_modifier_name)

        # color
        col.separator()
        col.label(text='Color')
        # enable color
        # if my_props.enable_color:
        #     for area in context.workspace.screens[0].areas:
        #         for space in area.spaces:
        #             if space.type == 'VIEW_3D':
        #                 space.shading.type = 'MATERIAL'

        # base color
        col.use_property_split = True
        col.prop(line_art_modifier, 'target_material', text='Base Color Material')
        if line_art_modifier.target_material is not None:
            col.prop(line_art_modifier.target_material.grease_pencil, 'color', text='Base Color')
        col.separator()

        # colors
        tints = get_gp_modifiers(modifier='GP_TINT')
        for tint in tints:
            row = col.row(align=True)
            row.use_property_split = False
            ot = row.operator('dskjal.linearttooleditmodifier', icon='CANCEL', text='')
            ot.modifier_name = tint.name
            ot.type = 'DELETE'
            row.prop(tint, 'color', text='')
            row.prop(tint, 'factor', slider=True)
            if is_edit_mode:
                row = col.row(align=True)
                ot = row.operator('dskjal.linearttooleditmodifier', text='Assign')
                ot.modifier_name = tint.name
                ot.type = 'ADD'
                ot = row.operator('dskjal.linearttooleditmodifier', text='Remove')
                ot.modifier_name = tint.name
                ot.type = 'REMOVE'
                col.separator(factor=2)
            row = col.row(align=True)
            col.separator()

        if is_edit_mode:
            col.separator()
            ot = col.operator('dskjal.linearttooladdmodifier', text="Add Color")                
            ot.modifier_type = 'GP_TINT'
            ot.modifier_name = tint_modifier_name


def gp_object_poll(self, object):
    return object.type == 'GPENCIL'

class DSKJAL_LINEART_TOOL_PROPS(bpy.types.PropertyGroup):
    gp_object : bpy.props.PointerProperty(name='gp_object', description='Grease Pencil Object', type=bpy.types.Object, poll=gp_object_poll)
    lineart_modifier : bpy.props.StringProperty(name='line_art_modifier', description='Line Art Modifier', default='Line Art')
    opacity_weight : bpy.props.FloatProperty(name='opacity_weight', description='Line opacity weight', default=1, min=0, max=1)
    thickness_weight : bpy.props.FloatProperty(name='thickness_weight', description='Line thickness weight', default=1, min=0, max=1)

classes = (
    DSKJAL_OT_LINEART_TOOL_AUTO_SETUP,
    DSKJAL_OT_LINEART_TOOL_FROM_ACTIVE_CAMERA_AND_LOCK,
    DSKJAL_OT_LINEART_TOOL_FREE_CAMERA,
    DSKJAL_OT_LINEART_TOOL_EDIT_MODIFIER,
    DSKJAL_OT_LINEART_TOOL_ADD_MODIFIER,
    DSKJAL_PT_LINEART_TOOL_UI,
    DSKJAL_LINEART_TOOL_PROPS
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.lineart_tool_props = bpy.props.PointerProperty(type=DSKJAL_LINEART_TOOL_PROPS)

def unregister():
    if hasattr(bpy.types.Scene, "lineart_tool_props"): del bpy.types.Scene.lineart_tool_props
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()