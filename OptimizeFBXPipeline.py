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

        layout.operator("scene.clear_scene")
        layout.operator("scene.import_fbx", text="导入FBX")
        layout.operator("object.add_decimate_modifier", text="减面设置")
        layout.operator("object.apply_decimate_modifier", text="应用减面")
        layout.operator("object.select_non_manifold_edges", text="补洞")
        layout.operator("scene.export_fbx", text="导出FBX")

# 清空场景
class EmptyScene(bpy.types.Operator):
    bl_idname = "scene.clear_scene"
    bl_label = "清空场景"

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

    def execute(self, context):
        bpy.ops.import_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}

# 导出FBX
class ExportFBXOperator(bpy.types.Operator):
    bl_idname = "scene.export_fbx"
    bl_label = "导出FBX场景"

    def execute(self, context):
        bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}

# 定义一个操作符用于添加 "Decimate" 修饰器
class AddDecimateModifierOperator(bpy.types.Operator):
    bl_idname = "object.add_decimate_modifier"
    bl_label = "减面设置"
    
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

    def execute(self,context):
        obj = context.active_object
        bpy.ops.object.modifier_apply(modifier="Decimate")
        return {'FINISHED'}

# 定义一个操作符用于选择非流形边
class SelectNonManifoldEdgesOperator(bpy.types.Operator):
    bl_idname = "object.select_non_manifold_edges"
    bl_label = "补洞"
    
    # 执行操作的函数
    def execute(self, context):
        # 切换到编辑模式
        bpy.ops.object.mode_set(mode='EDIT')
        # 切换选择边
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

        # 选择所有非流形边
        bpy.ops.mesh.select_non_manifold()

        # 补面
        bpy.ops.mesh.edge_face_add()
        return {'FINISHED'}

# 注册面板和操作符
def register():
    bpy.utils.register_class(CustomPanel)
    bpy.utils.register_class(EmptyScene)
    bpy.utils.register_class(ImportFBXOperator)
    bpy.utils.register_class(ExportFBXOperator)
    bpy.utils.register_class(AddDecimateModifierOperator)
    bpy.utils.register_class(ApplyDecimateModifierOperator)
    bpy.utils.register_class(SelectNonManifoldEdgesOperator)

# 注销面板和操作符
def unregister():
    bpy.utils.unregister_class(CustomPanel)
    bpy.utils.unregister_class(EmptyScene)
    bpy.utils.unregister_class(ImportFBXOperator)
    bpy.utils.unregister_class(ExportFBXOperator)
    bpy.utils.unregister_class(AddDecimateModifierOperator)
    bpy.utils.unregister_class(ApplyDecimateModifierOperator)
    bpy.utils.unregister_class(SelectNonManifoldEdgesOperator)

# 在脚本执行时调用注册函数
if __name__ == "__main__":
    register()
