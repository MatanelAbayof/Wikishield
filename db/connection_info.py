import os


# ---------------------------------------------------------------------------------------------------------------
def read_sql_user_name():
    """
    read SQL user name of this tool

    return SQL user name
    """

    file_path = os.path.expanduser("~/replica.my.cnf")
    with open(file_path, 'r') as f:
        lines = f.readlines()
        user_name_line = next(line for line in lines if line.strip().startswith('user = '))
        user_name = user_name_line.split('=')[-1].strip()
        return user_name