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
    "version" : (3, 1),
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
    la = get_active_line_art()
    if la == None:
        return default_filter_source
    
    return la.source_vertex_group

def get_active_line_art():
    idx = bpy.context.scene.lineart_tool_props.active_lineart_idx
    gp = bpy.context.scene.lineart_tool_props.gp_object
    if gp == None:
        return None
    if idx >= len(gp.grease_pencil_modifiers):
        return None
    
    for i in reversed(range(0, idx+1)):
        if gp.grease_pencil_modifiers[i].type == 'GP_LINEART':
            return gp.grease_pencil_modifiers[i]

    return None

def set_active_line_art(gp, line_art_name):
    idx = gp.grease_pencil_modifiers.find(line_art_name)
    if idx == -1:
        idx = bpy.context.scene.lineart_tool_props.active_lineart_idx - 1
        if idx == -1 and len(gp.grease_pencil_modifiers) != 0:
            idx = 0

    bpy.context.scene.lineart_tool_props.active_lineart_idx = idx

def add_lineart_modifier(gp, layer_name, filter_source):
    # assign new material
    material = bpy.data.materials.new(base_color_name)
    bpy.data.materials.create_gpencil_data(material)
    gp.data.materials.append(material)

    la = gp.grease_pencil_modifiers.new(name='Line Art', type='GP_LINEART')
    la.source_type = 'SCENE'
    la.target_layer = layer_name
    la.target_material = material
    la.source_vertex_group = filter_source
    return la

def create_lineart_grease_pencil():
    ob = bpy.context.active_object
    old_mode = 'OBJECT' if ob is None else ob.mode
    if ob is not None:
        bpy.ops.object.mode_set(mode='OBJECT')

    gp_data = bpy.data.grease_pencils.new('Line Art')
    layer = gp_data.layers.new('GP_Layer')
    layer.frames.new(bpy.context.scene.frame_current)
    
    gp = bpy.data.objects.new('Line Art', gp_data)
    bpy.context.scene.collection.objects.link(gp)
    gp.show_in_front = True
    filter_source = get_filter_source()
    add_lineart_modifier(gp, layer.info, filter_source)

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
    set_active_line_art(gp, 'Line Art')

    if ob is not None:
        bpy.ops.object.mode_set(mode=old_mode)

def get_lineart_gpencil(is_create=True):
    la = get_active_line_art()
    if la != None:
        return bpy.context.scene.lineart_tool_props.gp_object

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
    type : bpy.props.StringProperty() # type = {'GP', 'LINEART'}
  
    def execute(self, context):
        if self.type == 'GP':
            create_lineart_grease_pencil()
        elif self.type == 'LINEART':
            my_props = context.scene.lineart_tool_props
            if my_props.gp_object == None:
                raise Exception('gp_object is None')
            
            gp = my_props.gp_object
            data = gp.data
            la = add_lineart_modifier(gp, data.layers[0].info, get_filter_source())

            # reorder
            # context error work around
            old_active = context.active_object
            context.view_layer.objects.active = gp

            idx = 0
            for i in range(len(gp.grease_pencil_modifiers)):
                m = gp.grease_pencil_modifiers[i]
                if m.type == 'GP_LINEART':
                    bpy.ops.object.gpencil_modifier_move_to_index(index=idx, modifier=m.name)
                    idx += 1

            set_active_line_art(gp, la.name)
            context.view_layer.objects.active = old_active

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
        vg_name = gp.vertex_groups.new(name=vg_name).name
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
            if m.type == 'GP_LINEART':
                # delete material
                mat = m.target_material
                if mat is not None:
                    m.target_material = None
                    gp.data.materials.pop(index=gp.data.materials.find(mat.name))

            else:
                # delete line art vertex_group if other modifier does not refer it
                vg = m.vertex_group
                m.vertex_group = ''
                if vg is not None:
                    found = False
                    for mod in gp.grease_pencil_modifiers:
                        if mod.vertex_group == vg:
                            found = True
                            break

                    if not found:
                        idx = gp.vertex_groups.find(vg)
                        if idx != -1:
                            gp.vertex_groups.remove(gp.vertex_groups[idx])
                
            name = get_active_line_art().name
            gp.grease_pencil_modifiers.remove(m)
            set_active_line_art(gp, name)
        else:
            edit_vertex_group(modifier=m, type=self.type, weight=1)
        return {'FINISHED'}

class DSKJAL_OT_LINEART_TOOL_LAYER(bpy.types.Operator):
    bl_idname = 'dskjal.linearttoollayer'
    bl_label = 'Layer Operator'
    command : bpy.props.StringProperty() # command = {'UP', 'DOWN', 'DELETE', 'ADD'}
    layer_name : bpy.props.StringProperty()
    def execute(self, context):
        gp = get_lineart_gpencil()
        old_active = context.active_object
        context.view_layer.objects.active = gp

        if self.command == 'ADD':
            bpy.ops.gpencil.layer_add()
        else:
            layers = gp.data.layers
            idx = layers.find(self.layer_name)
            if idx != -1:
                layers.active_index = idx

            if self.command in ('UP', 'DOWN'):
                bpy.ops.gpencil.layer_move(type=self.command)
            elif self.command == 'DELETE':
                bpy.ops.gpencil.layer_remove()
            
        context.view_layer.objects.active = old_active

        return {'FINISHED'}

class DSKJAL_OT_LINEART_TOOL_SET_LINEART(bpy.types.Operator):
    bl_idname = 'dskjal.linearttoolsetlineart'
    bl_label = 'Set Line Art'
    modifier_name : bpy.props.StringProperty()
    def execute(self, context):
        set_active_line_art(context.scene.lineart_tool_props.gp_object, self.modifier_name)
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
        ot = col.operator('dskjal.linearttoolautosetup', text='Add Line Art Grease Pencil')
        ot.type = 'GP'
        col.separator(factor=3)
        # camera
        col.label(text='Camera')
        row = col.row(align=True)
        row.operator('dskjal.linearttoolfromactivecameraandlock', text='Lock')
        row.operator('dskjal.linearttoolfreecamera', text='Free')
        col.separator()

        # Grease Pencil
        col.label(text='Grease Pencil')
        col.prop_search(my_props, 'gp_object', bpy.data, 'objects', text='Grease Pencil')
        grease_pencil = my_props.gp_object
        if grease_pencil == None:
            return
        
        col.prop(grease_pencil, 'show_in_front')

        # Line Art
        col.label(text='Line Art')
        
        active_lineart = get_active_line_art()
        if active_lineart == None:
            col.separator()
            ot = col.operator('dskjal.linearttoolautosetup', text='Add Line Art Modifier')
            ot.type = 'LINEART'
            return

        # list line art modifiers
        la_modifiers = [m for m in grease_pencil.grease_pencil_modifiers if m.type == 'GP_LINEART']
        for m in la_modifiers:
            row = col.row(align=True)
            row.use_property_split = False
            ot = row.operator('dskjal.linearttooleditmodifier', icon='CANCEL', text='')
            ot.modifier_name = m.name
            ot.type = 'DELETE'
            if m == active_lineart:
                row.alert = True
            row.prop(m, 'name', text='')
            row.prop_search(m, 'target_layer', grease_pencil.data, 'layers', text='')
            row.alert = False
            row.prop(m, 'show_viewport', text='')
            row.prop(m, 'show_render', text='')
            ot = row.operator('dskjal.linearttoolsetlineart', text='', icon='RESTRICT_SELECT_OFF')
            ot.modifier_name = m.name

        col.separator()
        ot = col.operator('dskjal.linearttoolautosetup', text='Add Line Art Modifier')
        ot.type = 'LINEART'

        ob = context.active_object
        is_edit_mode = ob and ob.type in ('MESH', 'OBJECT') and context.active_object.mode == 'EDIT'

        col.separator(factor=2)
        row = col.row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.prop(my_props, 'lineart_ui_is_open', text='Line Art Settings', icon='TRIA_DOWN' if my_props.lineart_ui_is_open else 'TRIA_RIGHT', emboss=False)
        if my_props.lineart_ui_is_open:
            box = col.box()
            box.prop(active_lineart, 'source_type')
            if active_lineart.source_type == 'COLLECTION':
                box.prop(active_lineart, 'source_collection')
            elif active_lineart.source_type == 'OBJECT':
                box.prop(active_lineart, 'source_object')
                
            #box.prop(active_lineart, 'source_vertex_group', text="Filter Source")

            # Edge type
            box.label(text='Edge Types')
            row = box.row(align=True)
            row.use_property_split = False
            row.prop(active_lineart, 'use_contour', text='Contour', toggle=1)
            row.prop(active_lineart, 'use_material', text='Material Boundaries', toggle=1)
            row = box.row(align=True)
            row.use_property_split = False

            row.prop(active_lineart, 'use_intersection', text='Intersections', toggle=1)
            if is_edit_mode:
                box.separator()

            box.use_property_split = False
            box.prop(active_lineart, 'use_edge_mark', text='Edge Marks', toggle=1)
            if is_edit_mode:
                row = box.row(align=True)
                row.use_property_split = False
                ot = row.operator('mesh.mark_freestyle_edge', text="Mark")
                ot = row.operator('mesh.mark_freestyle_edge', text='Clear')
                ot.clear = True

            if is_edit_mode:
                box.separator()
            box.use_property_split = False
            row = box.row(align=True)
            row.prop(active_lineart, 'use_crease', text='Crease', toggle=1)
            row.prop(active_lineart, 'crease_threshold', text='', slider=True)

            # options
            row = box.row()
            row.use_property_split = False
            row.alignment = 'LEFT'
            row.prop(my_props, 'lineart_option_is_open', text='Option', icon='TRIA_DOWN' if my_props.lineart_option_is_open else 'TRIA_RIGHT', emboss=False)
            if my_props.lineart_option_is_open:
                cbox = box.box()
                cbox.use_property_split = True
                cbox.prop(active_lineart, 'use_edge_overlap', text='Overlapping Edge As Contour')
                cbox.prop(active_lineart, 'use_object_instances')
                cbox.prop(active_lineart, 'use_clip_plane_boundaries')
                
            # occlusion 
            row = box.row()
            row.use_property_split = False
            row.alignment = 'LEFT'
            row.prop(my_props, 'occlusion_is_open', text='Occlusion', icon='TRIA_DOWN' if my_props.occlusion_is_open else 'TRIA_RIGHT', emboss=False)
            if my_props.occlusion_is_open:
                cbox = box.box()
                cbox.use_property_split = True
                cbox.prop(active_lineart, 'use_multiple_levels', text='Range')
                cbox.prop(active_lineart, 'level_start', text='Level')
                cbox.prop(active_lineart, 'use_transparency')
                row = cbox.row()
                row.active = active_lineart.use_transparency
                for i in range(8):
                    row.prop(active_lineart, "use_transparency_mask", index=i, toggle=1, text=str(i))
                ccol = cbox.column()
                ccol.active = active_lineart.use_transparency
                ccol.prop(active_lineart, 'use_transparency_match', text='Match All Masks')

            # chaining
            row = box.row()
            row.use_property_split = False
            row.alignment = 'LEFT'
            row.prop(my_props, 'chaining_is_open', text='Chaining', icon='TRIA_DOWN' if my_props.chaining_is_open else 'TRIA_RIGHT', emboss=False)
            if my_props.chaining_is_open:
                cbox = box.box()
                cbox.use_property_split = True
                cbox.prop(active_lineart, 'use_fuzzy_intersections')
                cbox.prop(active_lineart, 'use_fuzzy_all')
                cbox.prop(active_lineart, 'chaining_image_threshold')
                cbox.prop(active_lineart, 'split_angle', slider=True)


        col.use_property_split = True

        row = col.row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.prop(my_props, 'layer_is_open', text='Layers', icon='TRIA_DOWN' if my_props.layer_is_open else 'TRIA_RIGHT', emboss=False)
        if my_props.layer_is_open:
            for l in reversed(grease_pencil.data.layers):
                row = col.row(align=True)
                row.use_property_split = False
                ot = row.operator('dskjal.linearttoollayer', text='', icon='CANCEL')
                ot.command = 'DELETE'
                ot.layer_name = l.info
                row.prop(l, 'info', text='')
                row.prop(l, 'opacity', text='')
                row.prop(l, 'hide', text='')
                ot = row.operator('dskjal.linearttoollayer', text='', icon='TRIA_UP')
                ot.command = 'UP'
                ot.layer_name = l.info
                ot = row.operator('dskjal.linearttoollayer', text='', icon='TRIA_DOWN')
                ot.command = 'DOWN'
                ot.layer_name = l.info


            col.separator()
            ot = col.operator('dskjal.linearttoollayer', text='Add New Layer')
            ot.command = 'ADD'
        
        def print_modifier(modifier, modifier_name, name):
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
                ot = col.operator('dskjal.linearttooladdmodifier', text="Add "+name)                
                ot.modifier_type = modifier
                ot.modifier_name = modifier_name

        # opacity
        row = col.row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.prop(my_props, 'opacity_is_open', text='Opacity', icon='TRIA_DOWN' if my_props.opacity_is_open else 'TRIA_RIGHT', emboss=False)
        if my_props.opacity_is_open:
            col.prop(active_lineart, 'opacity', text='Base Opacity')
            col.separator()
            print_modifier(modifier='GP_OPACITY', modifier_name=opacity_modifier_name, name='Opacity')

        # thickness
        row = col.row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.prop(my_props, 'thickness_is_open', text='Thickness', icon='TRIA_DOWN' if my_props.thickness_is_open else 'TRIA_RIGHT', emboss=False)
        if my_props.thickness_is_open:
            col.prop(active_lineart, 'thickness', text='Base Thickness')
            col.separator()
            print_modifier(modifier='GP_THICK', modifier_name=thickness_modifier_name, name='Thickness')

        # color
        row = col.row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.prop(my_props, 'color_is_open', text='Color', icon='TRIA_DOWN' if my_props.color_is_open else 'TRIA_RIGHT', emboss=False)
        if my_props.color_is_open:
            # base color
            col.use_property_split = True
            #col.prop(active_lineart, 'target_material', text='Base Color Material')
            if active_lineart.target_material is not None:
                col.prop(active_lineart.target_material.grease_pencil, 'color', text='Base Color')
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
    active_lineart_idx : bpy.props.IntProperty(name='active_lineart_idx', default=0, min=-1)

    # ui
    lineart_ui_is_open : bpy.props.BoolProperty(name='lineart_ui_is_open', default=True)
    layer_is_open : bpy.props.BoolProperty(name='layer_is_open', default=False)
    lineart_option_is_open : bpy.props.BoolProperty(name='lineart_option_is_open', default=True)
    occlusion_is_open : bpy.props.BoolProperty(name='occlusion_is_open', default=False)
    chaining_is_open : bpy.props.BoolProperty(name='chaining_is_open', default=False)
    opacity_is_open : bpy.props.BoolProperty(name='opacity_is_open', default=True)
    thickness_is_open : bpy.props.BoolProperty(name='thickness_is_open', default=True)
    color_is_open : bpy.props.BoolProperty(name='color_is_open', default=True)

classes = (
    DSKJAL_OT_LINEART_TOOL_AUTO_SETUP,
    DSKJAL_OT_LINEART_TOOL_FROM_ACTIVE_CAMERA_AND_LOCK,
    DSKJAL_OT_LINEART_TOOL_FREE_CAMERA,
    DSKJAL_OT_LINEART_TOOL_EDIT_MODIFIER,
    DSKJAL_OT_LINEART_TOOL_ADD_MODIFIER,
    DSKJAL_OT_LINEART_TOOL_LAYER,
    DSKJAL_OT_LINEART_TOOL_SET_LINEART,
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