# поиск слов в БД
def find_usage(text: str, CONNECTION):
    usage_dict = CONNECTION.execute(
        f'''
        select * from subtitles
        where content like "%{text}%";
        '''
    ).fetchall()
    return usage_dict
