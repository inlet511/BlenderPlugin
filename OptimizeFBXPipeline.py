bl_info = {
    "name": "Optimize FBX",
    "author": "Ken An",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > 优化流程",
    "description": "优化FBX模型,减面、补洞",
    "warning": "",
    "doc_url": "",
    "category": "Pipeline",
}

import bpy
import bmesh

# 创建一个自定义面板类
class CustomPanel(bpy.types.Panel):
    bl_label = "优化模型"  # 面板的名称
    bl_idname = "PT_CustomPanel"  # 面板的唯一标识符
    bl_space_type = 'VIEW_3D'  # 面板所在区域
    bl_region_type = 'UI'  # 面板所在区域的类型
    bl_category = "优化流程"  # 面板所在选项卡的名称

    # 绘制面板内容
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("scene.clear_scene",text = "清空场景")
        layout.operator("scene.import_fbx", text="导入FBX")
        layout.operator("object.delete_loose_element", text="删除游离元素")
        layout.operator("object.dissolve_degenerated", text="融并清理")
        layout.prop(scene,"merge_threshold")
        layout.operator("object.merge_by_distance", text="按间距合并")
        layout.operator("object.fill_holes", text="填补漏洞")
        layout.operator("object.add_decimate_modifier", text="减面设置")
        layout.operator("object.apply_decimate_modifier", text="应用减面")
        layout.operator("scene.export_fbx", text="导出FBX")

# 清空场景
class EmptyScene(bpy.types.Operator):
    bl_idname = "scene.clear_scene"
    bl_label = "清空场景"
    bl_description = "清空整个场景，开始时进行操作"

    def execute(self,context):
        # 获取当前激活对象
        obj = bpy.context.active_object
        # 如果有激活对象
        if obj is not None:
            bpy.ops.object.mode_set(mode='OBJECT')

        if len(bpy.data.objects) > 0:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
        return {'FINISHED'}


# 导入FBX
class ImportFBXOperator(bpy.types.Operator):
    bl_idname = "scene.import_fbx"
    bl_label = "导入FBX场景"
    bl_description = "导入FBX文件"

    def execute(self, context):
        bpy.ops.import_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}

# 导出FBX
class ExportFBXOperator(bpy.types.Operator):
    bl_idname = "scene.export_fbx"
    bl_label = "导出FBX场景"
    bl_description = "导出FBX文件"

    def execute(self, context):
        bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}

# 删除游离元素
class DeleteLooseOperator(bpy.types.Operator):
    bl_idname = "object.delete_loose_element"
    bl_label = "删除游离元素"
    bl_description = "删除游离的点、边"

    def execute(self, context):
         # 获取当前选中的对象
        obj = context.active_object
        if obj is not None:
            # 切换到编辑模式
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete_loose(use_faces=True)
        return {'FINISHED'}


# 融合面积为零的面以及长度为零的边
class DissolveDegeneratedOperator(bpy.types.Operator):
    bl_idname = "object.dissolve_degenerated"
    bl_label = "融并清理"
    bl_description = "清理面积为零的面以及长度为零的边"

    def execute(self, context):
        # 获取当前选中的对象
        obj = context.active_object
        if obj is not None:
            # 切换到编辑模式
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.dissolve_degenerate()
        return {'FINISHED'}

# 按间距合并
class MergeByDistanceOperator(bpy.types.Operator):
    bl_idname = "object.merge_by_distance"
    bl_label = "按间距合并"
    bl_description = "合并重合的点(按照距离)"

    
    def execute(self,context):
        distance = 0.01
         # 获取当前选中的对象
        meshes = set(o.data for o in context.selected_objects
                      if o.type == 'MESH')

        bm = bmesh.new()

        for m in meshes:
            bm.from_mesh(m)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
            bm.to_mesh(m)
            m.update()
            bm.clear()

        bm.free()
        return {'FINISHED'}

# 填补漏洞
class FillHoleOperator(bpy.types.Operator):
    bl_idname = "object.fill_holes"
    bl_label = "填补漏洞"
    bl_description = "填补破开的洞"

    def execute(self,context):
        # 获取当前选中的对象
        obj = context.active_object
        if obj is not None:
            # 切换到编辑模式
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.fill_holes()
        return {'FINISHED'}

# 定义一个操作符用于添加 "Decimate" 修饰器
class AddDecimateModifierOperator(bpy.types.Operator):
    bl_idname = "object.add_decimate_modifier"
    bl_label = "减面设置"
    bl_description = "给对象添加减面修改器"
    
    # 执行操作的函数
    def execute(self, context):
        # 获取当前选中的对象
        obj = context.active_object

        # 切换到修改器面板
        C = bpy.context
        for area in C.screen.areas:
            if area.type == 'PROPERTIES' and C.object.type not in ('LIGHT_PROBE', 'CAMERA', 'LIGHT', 'SPEAKER'):
                # Set it the active space
                area.spaces.active.context = 'MODIFIER' # 'VIEW_LAYER', 'SCENE' etc.
                break # OPTIONAL

        # 添加 "Decimate" 修饰器
        modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
        return {'FINISHED'}

# 应用减面设置
class ApplyDecimateModifierOperator(bpy.types.Operator):
    bl_idname="object.apply_decimate_modifier"
    bl_label="应用减面"
    bl_description = "应用减面修改器"

    def execute(self,context):
        obj = context.active_object
        bpy.ops.object.modifier_apply(modifier="Decimate")
        return {'FINISHED'}




# 注册面板和操作符
def register():
    bpy.utils.register_class(CustomPanel)
    bpy.utils.register_class(EmptyScene)
    bpy.utils.register_class(ImportFBXOperator)
    bpy.utils.register_class(ExportFBXOperator)
    bpy.utils.register_class(AddDecimateModifierOperator)
    bpy.utils.register_class(ApplyDecimateModifierOperator)
    bpy.utils.register_class(DeleteLooseOperator)
    bpy.utils.register_class(DissolveDegeneratedOperator)
    bpy.utils.register_class(MergeByDistanceOperator)
    bpy.utils.register_class(FillHoleOperator)

    bpy.types.Scene.merge_threshold = bpy.props.FloatProperty(name="merge_threshold", default=0.001)


# 注销面板和操作符
def unregister():
    bpy.utils.unregister_class(CustomPanel)
    bpy.utils.unregister_class(EmptyScene)
    bpy.utils.unregister_class(ImportFBXOperator)
    bpy.utils.unregister_class(ExportFBXOperator)
    bpy.utils.unregister_class(AddDecimateModifierOperator)
    bpy.utils.unregister_class(ApplyDecimateModifierOperator)
    bpy.utils.unregister_class(DeleteLooseOperator)
    bpy.utils.unregister_class(DissolveDegeneratedOperator)
    bpy.utils.unregister_class(MergeByDistanceOperator)
    bpy.utils.unregister_class(FillHoleOperator)

    del bpy.types.Scene.merge_threshold


# 在脚本执行时调用注册函数
if __name__ == "__main__":
    register()
