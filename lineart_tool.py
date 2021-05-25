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
    "version" : (1, 2),
    "blender" : (2, 93, 0),
    "location" : "View3D > Sidebar > Tool > Line Art Tool",
    "description" : "",
    "warning" : "",
    "wiki_url" : "https://github.com/dskjal/Line-Art-Tool",
    "tracker_url" : "",
    "category" : "Mesh"
}

opacity_vertex_group_suffix = '_opacity'
thickness_vertex_group_suffix = '_thickness'
opacity_modifier_name = 'lineart_tool_hide'
thickness_modifier_name = 'lineart_tool_thickness'
tint_modifier_name = 'lineart_tool_tint'
base_color_name = 'lineart_tool_base_color'

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

    # thickness modifier
    thick = gp.grease_pencil_modifiers.new(name=thickness_modifier_name, type='GP_THICK')
    thick.normalize_thickness = True
    thick_vg_name = bpy.context.scene.lineart_tool_props.filter_source + thickness_vertex_group_suffix
    gp.vertex_groups.new(name=thick_vg_name)
    thick.vertex_group = thick_vg_name

    # opacity modifier
    opacity = gp.grease_pencil_modifiers.new(name=opacity_modifier_name, type='GP_OPACITY')
    opacity.factor = 0
    opacity_vg_name = bpy.context.scene.lineart_tool_props.filter_source + opacity_vertex_group_suffix
    gp.vertex_groups.new(name=opacity_vg_name)
    opacity.vertex_group = opacity_vg_name

    bpy.context.scene.lineart_tool_props.gp_object = gp
    bpy.context.scene.lineart_tool_props.lineart_modifier = 'Line Art'

    if ob is not None:
        bpy.ops.object.mode_set(mode=old_mode)

def get_lineart_gpencil():
    gp = bpy.context.scene.lineart_tool_props.gp_object
    la_name = bpy.context.scene.lineart_tool_props.lineart_modifier
    if gp != None:
        if gp.grease_pencil_modifiers.find(la_name) != -1 and gp.grease_pencil_modifiers[la_name].type == 'GP_LINEART':
            return gp

    return create_lineart_grease_pencil()

def get_lineart_modifier():
    gp = get_lineart_gpencil()
    return gp.grease_pencil_modifiers[bpy.context.scene.lineart_tool_props.lineart_modifier]

def create_lineart_vertex_group(ob, filter_source):
    hide_name = filter_source + opacity_vertex_group_suffix
    if ob.vertex_groups.find(hide_name) == -1:
        ob.vertex_groups.new(name=hide_name)
    thick_name = filter_source + thickness_vertex_group_suffix
    if ob.vertex_groups.find(thick_name) == -1:
        ob.vertex_groups.new(name=thick_name)

    # grease penciil
    vgs = [vg.name for vg in ob.vertex_groups if vg.name.startswith(filter_source)]
    gp = get_lineart_gpencil()
    for vg in vgs:
        if gp.vertex_groups.find(vg) == -1:
            gp.vertex_groups.new(name=vg)


def get_lineart_vertex_group(ob, vertex_group_name):
    id = ob.vertex_groups.find(vertex_group_name)
    if id == -1:
        return ob.vertex_groups.new(name=vertex_group_name)
    else:
        return ob.vertex_groups[id]
    
def get_gp_modifier(gp, name, type):
    for m in gp.grease_pencil_modifiers:
        if m.name == name:
            return m
    
    return gp.grease_pencil_modifiers.new(name=name, type=type)

def get_thickness_modifier():
    gp = get_lineart_gpencil()
    return get_gp_modifier(gp, thickness_modifier_name, type='GP_THICK')
    
def get_gp_tint_modifiers():
    gp = get_lineart_gpencil()
    return [m for m in gp.grease_pencil_modifiers if m.name.startswith(tint_modifier_name)]

# modifier={'OPACITY', 'THICK', 'TINT'}
# type={'ADD', 'REMOVE'}
def edit_vertex_group(modifier, type, weight=1, tint_name=''):
    ob = bpy.context.active_object
    bpy.ops.object.mode_set(mode='OBJECT')

    selected_verts = [v.index for v in ob.data.vertices if v.select]
    if not selected_verts: # if selected_verts is empty
        bpy.ops.object.mode_set(mode='EDIT')
        return
    
    filter_source = bpy.context.scene.lineart_tool_props.filter_source
    if modifier == 'OPACITY':
        edit_vertex_group_name = filter_source + opacity_vertex_group_suffix
    elif modifier == 'THICK':
        edit_vertex_group_name = filter_source + thickness_vertex_group_suffix
    elif modifier == 'TINT':
        edit_vertex_group_name = filter_source + tint_name

    create_lineart_vertex_group(ob, filter_source)
    vg = get_lineart_vertex_group(ob, edit_vertex_group_name)
    if type == 'ADD':
        vg.add(selected_verts, weight, 'REPLACE')
    elif type == 'REMOVE':
        vg.remove(selected_verts)
    else:
        raise Exception('edit_vertex_group(): wrong type')

    # set lineart modifiers
    lineart = get_lineart_modifier()
    lineart.source_vertex_group = filter_source

    gp = get_lineart_gpencil()
    # add gpencil vertex group
    if gp.vertex_groups.find(edit_vertex_group_name) == -1:
        gp.vertex_groups.new(name=edit_vertex_group_name)

    # set vertex group
    if modifier == 'OPACITY':
        m = get_gp_modifier(gp, name=opacity_modifier_name, type='GP_OPACITY')
    elif modifier == 'THICK':
        m = get_gp_modifier(gp, name=thickness_modifier_name, type='GP_THICK')
    elif modifier == 'TINT':
        m = get_gp_modifier(gp, name=tint_name, type='GP_TINT')

    m.vertex_group = edit_vertex_group_name

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

class DSKJAL_OT_LINEART_TOOL_OPACITY(bpy.types.Operator):
    bl_idname = "dskjal.linearttoolopacity"
    bl_label = "Opacity"
    weight : bpy.props.FloatProperty()
    type : bpy.props.StringProperty()
    def execute(self, context):
        edit_vertex_group(modifier='OPACITY', type=self.type, weight=self.weight)
        return {'FINISHED'}

class DSKJAL_OT_LINEART_TOOL_THICKNESS(bpy.types.Operator):
    bl_idname = "dskjal.linearttoolthickness"
    bl_label = "Set thickness weight"
    weight : bpy.props.FloatProperty()
    def execute(self, context):
        if self.weight == 0:
            edit_vertex_group(modifier='THICK', type='REMOVE')
        else:
            edit_vertex_group(modifier='THICK', type='ADD', weight=self.weight)
        return {'FINISHED'}    

class DSKJAL_OT_LINEART_TOOL_ADD_TINT(bpy.types.Operator):
    bl_idname = "dskjal.linearttooladdtint"
    bl_label = "Add color"
    def execute(self, context):
        gp = get_lineart_gpencil()
        tint = gp.grease_pencil_modifiers.new(name=tint_modifier_name, type='GP_TINT')
        tint.color = (0, 0, 0)
        filter_source = context.scene.lineart_tool_props.filter_source
        tint_vg_name = filter_source + tint.name
        gp.vertex_groups.new(name=tint_vg_name)
        tint.vertex_group = tint_vg_name
        ob = context.active_object
        if ob.vertex_groups.find(tint.name) == -1:
            ob.vertex_groups.new(name=tint_vg_name)
            create_lineart_vertex_group(ob, context.scene.lineart_tool_props.filter_source)
        else:
            # clear vertex group
            ob.vertex_groups.remove(ob.vertex_groups[tint.name])
            ob.vertex_groups.new(name=tint_vg_name)
            
        return {'FINISHED'}

# type = {'ADD', 'REMOVE', 'DELETE'}
# remove tint modifier if type == 'DELETE' 
class DSKJAL_OT_LINEART_TOOL_TINT(bpy.types.Operator):
    bl_idname = 'dskjal.linearttooltint'
    bl_label = 'Tint'
    tint_name : bpy.props.StringProperty()
    type : bpy.props.StringProperty()
    def execute(self, context):
        if self.type == 'DELETE':
            gp = get_lineart_gpencil()
            gp.grease_pencil_modifiers.remove(gp.grease_pencil_modifiers[self.tint_name])
        else:
            edit_vertex_group(modifier='TINT', type=self.type, weight=1, tint_name=self.tint_name)
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
        col.separator()
        col.separator()
        col.separator()
        # camera
        col.label(text='Camera')
        row = col.row(align=True)
        row.operator('dskjal.linearttoolfromactivecameraandlock', text='Lock')
        row.operator('dskjal.linearttoolfreecamera', text='Free')
        col.separator()

        # Line Art
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
        col.prop(my_props, 'filter_source')

        # Edge type
        col.separator()
        col.separator()
        col.label(text='Edge Types')
        row = col.row(align=True)
        row.use_property_split = False
        row.prop(line_art_modifier, 'use_contour', text='Contour', toggle=1)
        row.prop(line_art_modifier, 'use_material', text='Material Boundaries', toggle=1)
        row = col.row(align=True)
        row.use_property_split = False

        row.prop(line_art_modifier, 'use_edge_mark', text='Edge Marks', toggle=1)
        row.prop(line_art_modifier, 'use_intersection', text='Intersections', toggle=1)

        col.separator()
        col.use_property_split = False
        col.prop(line_art_modifier, 'use_crease', text='Crease', toggle=1)
        col.prop(line_art_modifier, 'crease_threshold', text='', slider=True)

        col.separator()

        thick = None
        opacity = None
        if grease_pencil is not None:
            thick = get_gp_modifier(gp=grease_pencil, name=thickness_modifier_name, type='GP_THICK')
            opacity = get_gp_modifier(gp=grease_pencil, name=opacity_modifier_name, type='GP_OPACITY')
            
        ob = context.active_object
        if ob and ob.type in ('MESH', 'OBJECT') and context.active_object.mode == 'EDIT':
            # Edit mode
            # opacity
            col.separator()
            col.label(text='Opacity')
            if opacity is not None:
                col.prop(line_art_modifier, 'opacity', text='Base Opacity')
                col.prop(opacity, 'factor', text='Factor', slider=True)
                col.separator()
                col.prop(my_props, 'opacity_weight', text='Weight', slider=True)
                row = col.row(align=True)
                opacity_ot = row.operator('dskjal.linearttoolopacity', text='Assign')
                opacity_ot.type = 'ADD'
                opacity_ot.weight = my_props.opacity_weight
                opacity_ot = row.operator('dskjal.linearttoolopacity', text='Remove')
                opacity_ot.type = 'REMOVE'

            # thickness
            col.separator()
            col.separator()
            col.label(text='Thickness')
            if thick is not None:
                col.prop(line_art_modifier, 'thickness', text='Base Thickness')
                col.prop(thick, 'thickness', text='Thickness')
                col.separator()
                col.prop(my_props, 'thickness_weight', text='Weight', slider=True)
                row = col.row(align=True)
                thick_ot = row.operator('dskjal.linearttoolthickness', text='Assign')
                thick_ot.weight = my_props.thickness_weight
                thick_ot = row.operator('dskjal.linearttoolthickness', text='Remove')
                thick_ot.weight = 0

            # color
            col.separator()
            col.use_property_split = True
            col.label(text='Color')
            if grease_pencil is not None:
                # base color
                col.prop(grease_pencil.data.materials[base_color_name].grease_pencil, 'color', text='Base Color')
                col.separator()
                
                tints = get_gp_tint_modifiers()
                for tint in tints:
                    row = col.row(align=True)
                    row.use_property_split = False
                    ot = row.operator('dskjal.linearttooltint', icon='CANCEL', text='')
                    ot.tint_name = tint.name
                    ot.type = 'DELETE'
                    row.prop(tint, 'color', text='')
                    col.use_property_split = False
                    col.prop(tint, 'factor', slider=True)

                    col.separator()
                    row = col.row(align=True)
                    ot = row.operator('dskjal.linearttooltint', text='Assign')
                    ot.tint_name = tint.name
                    ot.type = 'ADD'
                    ot = row.operator('dskjal.linearttooltint', text='Remove')
                    ot.tint_name = tint.name
                    ot.type = 'REMOVE'
                    col.separator()
                    col.separator()
                    col.separator()
                    
                col.separator()
                col.operator('dskjal.linearttooladdtint', text="Add Color")
        else:
            col.use_property_split = True
            # Object mode
            # opacity
            col.label(text='Opacity')
            if opacity is not None:
                col.prop(line_art_modifier, 'opacity', text='Base Opacity')
                col.prop(opacity, 'factor', text='Factor', slider=True)

            # thickness
            col.separator()
            col.label(text='Thickness')
            if thick is not None:
                col.prop(line_art_modifier, 'thickness', text='Base Thickness')
                col.prop(thick, 'thickness', text='Thickness')

            # color
            col.separator()
            col.label(text='Color')
            # enable color
            # if my_props.enable_color:
            #     for area in context.workspace.screens[0].areas:
            #         for space in area.spaces:
            #             if space.type == 'VIEW_3D':
            #                 space.shading.type = 'MATERIAL'

            tints = get_gp_tint_modifiers()
            # base color
            col.prop(grease_pencil.data.materials[base_color_name].grease_pencil, 'color', text='Base Color')
            col.separator()

            for tint in tints:
                row = col.row(align=True)
                row.use_property_split = False
                ot = row.operator('dskjal.linearttooltint', icon='CANCEL', text='')
                ot.tint_name = tint.name
                ot.type = 'DELETE'
                row.prop(tint, 'color', text='')
                col.use_property_split = False
                col.prop(tint, 'factor', slider=True)
                row = col.row(align=True)
                col.separator()


def gp_object_poll(self, object):
    return object.type == 'GPENCIL'

class DSKJAL_LINEART_TOOL_PROPS(bpy.types.PropertyGroup):
    gp_object : bpy.props.PointerProperty(name='gp_object', description='Grease Pencil Object', type=bpy.types.Object, poll=gp_object_poll)
    lineart_modifier : bpy.props.StringProperty(name='line_art_modifier', description='Line Art Modifier', default='Line Art')
    filter_source : bpy.props.StringProperty(name='filter_source', description='Filter Source', default='lineart_')
    opacity_weight : bpy.props.FloatProperty(name='opacity_weight', description='Line opacity weight', default=1, min=0, max=1)
    thickness_weight : bpy.props.FloatProperty(name='thickness_weight', description='Line thickness weight', default=1, min=0, max=1)

classes = (
    DSKJAL_OT_LINEART_TOOL_AUTO_SETUP,
    DSKJAL_OT_LINEART_TOOL_FROM_ACTIVE_CAMERA_AND_LOCK,
    DSKJAL_OT_LINEART_TOOL_FREE_CAMERA,
    DSKJAL_OT_LINEART_TOOL_OPACITY,
    DSKJAL_OT_LINEART_TOOL_THICKNESS,
    DSKJAL_OT_LINEART_TOOL_TINT,
    DSKJAL_OT_LINEART_TOOL_ADD_TINT,
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