import configparser
import os


class Templater():
    template_folder = 'templates'
    content = None

    def __init__(self):
        self.content = self.get_config('Test_temp')

    def new_template(self, name):
        path = self.template_folder + '\\' + name + '.tpl'
        self.content = configparser.ConfigParser()
        self.content.add_section('global_tags')
        self.content.set('global_tags', 'Дозатор муки', 'Reset_Silos_Area,Системы_шкаф_Q1_Готовы')
        self.content.set('global_tags', 'Дозатор сахара', 'Reset_Silos_Area,Системы_шкаф_Q1_Готовы')
        self.content.add_section('local_tags')
        self.content.add_section('replacement')
        self.content.add_section('comments')

        with open(path, 'w') as config_file:
            self.content.write(config_file)

    def get_list_sections(self):
        for item in self.content.sections():
            print(self.content.options(item))
        return self.content.sections()

    def get_config(self, name):
        path = self.template_folder + '\\' + name + '.tpl'
        if os.path.exists(path):
            config = configparser.ConfigParser()
            config.read(path)
            return config

def main():
    temp = Templater()
    temp.get_list_sections()
    # for item in temp.get_list_sections():
    #     print(temp.get(item))

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
