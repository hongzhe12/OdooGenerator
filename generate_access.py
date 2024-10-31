def generate_access_control(model_name):
    # 替换点为下划线
    formatted_model_name = model_name.replace('.', '_')

    # 生成内部用户访问控制
    user_access_control = f"""access_{formatted_model_name}_user,{model_name}.user,model_{formatted_model_name},base.group_user,1,1,1,1\n"""

    # 生成公共用户访问控制
    public_access_control = f"""access_{formatted_model_name}_public,{model_name}.public,model_{formatted_model_name},base.group_public,1,0,0,0\n"""

    return user_access_control + public_access_control

def g_access(model_name_lists:list):
    str_list = ["id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"]
    model_name_lists = [model_name_lists]  # 这里可以添加更多的模型名
    for i in model_name_lists:
        access_config = generate_access_control(i)
        str_list.append(access_config)
    return "\n".join(str_list)

if __name__ == "__main__":
    print(g_access('operation.manual'))
