#!/usr/bin/python
# -*- coding: latin-1 -*-

import yaml
import urwid
import random
import subprocess
import sys

# playbook_filename='playbook.yml'

## Definizione dell'item class
class ItemWidget (urwid.WidgetWrap):

    def __init__ (self, task):
        try:
            self.content = task['name']
            self.dest = "task"
            if task['selected'] == '0':
                self.selected = ''
                foreground = 'proj'
                focused = 'proj_focus'
            else:
                self.selected = 'X'
                foreground = 'proj_selected'
                focused = 'proj_focus_selected'
        except KeyError:
            self.content = 'Include: ' + task['include']
            foreground = 'proj_include'
            focused = 'proj_include'
            self.desc = ''
            self.selected = ''

        proj = urwid.Text(self.content, align='left')
        desc = urwid.Text('')
        due = urwid.Text(self.selected, align='left')

        item = urwid.AttrMap(urwid.Columns([
            ('fixed', 30, urwid.AttrWrap(proj, foreground, focused)),
            due
        ]), 'body', 'body_focus')

        urwid.WidgetWrap.__init__(self, item)

    def selectable (self):
        if self.content == "Include":
            return False
        return True

    def keypress(self, size, key):
        return key


def main ():

    palette = [
        ('proj', '', '', ''),
        ('proj_include', 'light gray', 'dark gray', ''),
        ('proj_focus', '', 'dark blue', ''),
        ('proj_selected', 'light magenta', '', ''),
        ('proj_focus_selected', 'light magenta', 'dark blue', ''),
        ('body','', '', ''),
        ('body_focus', '', 'dark gray', ''),
        ('head','light red', 'black'),
    ]

    COMMAND_LINE_ARGS=sys.argv
    for arg in COMMAND_LINE_ARGS:
        if ".yml" in arg:
            playbook_filename = arg
            break

    try:
        with open(playbook_filename, 'r') as f:
            doc = yaml.load(f)
    except IOError:
        print "Error: " + playbook_filename + " not exists!"
        sys.exit(1)
    except UnboundLocalError:
        print "Error: playbook filename not found!"
        sys.exit(2)

    tasks = doc[0]['tasks']
    for task in tasks:
        task['selected'] = '0'

    def keystroke (input):
        if input in ('r', 'R'):
            raise urwid.ExitMainLoop()

        if input in ('enter', 's', 'S') :
            item_focused = listbox.get_focus()
            focus = item_focused[0].content
            try:
                if tasks[item_focused[1]]['name'] != "":
                    if tasks[item_focused[1]]['selected'] == '0':
                        tasks[item_focused[1]]['selected'] = '1'
                    else:
                        tasks[item_focused[1]]['selected'] = '0'
            except KeyError:
                focus = ""
            view.set_header(urwid.AttrWrap(urwid.Text(
                'selected: %s' % str(focus)), 'head'))
            refresh()

    def refresh():
        walker[:] = map(ItemWidget, tasks)

    def tag_playbook(tag):
        print 'Custom tag: ' + tag

        with open(playbook_filename) as f2:
             list_task = yaml.load(f2)

        for task in tasks:
            if task["selected"] == "1":
                for task_play in list_task[0]['tasks']:
                    try:
                        if task_play['name'] == task['name']:
                            if 'tags' in task_play.keys():
                                task_play['tags'] = task_play['tags'] + ',' + tag
                            else:
                                task_play['tags'] = tag
                    except KeyError:
                        continue

        #print(list_task)

        with open(playbook_filename, "w") as f2:
            yaml.dump(list_task, f2, default_flow_style=False)


    def run_playbook(tag):
        print 'Running playbook:'
        my_command = 'ansible-playbook --tags ' + tag + ' ' + ' '.join(COMMAND_LINE_ARGS[1:])
        print 'CMD: ' + my_command
        sub_process = subprocess.Popen(my_command, close_fds=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while sub_process.poll() is None:
            out = sub_process.stdout.read(1)
            sys.stdout.write(out)
            sys.stdout.flush()

    def remove_tag(tag):
        with open(playbook_filename) as f2:
             list_task = yaml.load(f2)

        for task_play in list_task[0]['tasks']:
            try:
                if task_play['tags'].find(tag) != -1:
                    task_play['tags'] = task_play['tags'].replace(',' + tag, '')
                    task_play['tags'] = task_play['tags'].replace(tag, '')
                    if task_play['tags'] == '':
                        del task_play['tags']
            except:
                continue

        with open(playbook_filename, "w") as f2:
            yaml.dump(list_task, f2, default_flow_style=False)

        #print(list_task)

    header = urwid.AttrMap(urwid.Text('selected:'), 'head')
    walker = urwid.SimpleListWalker([])
    listbox = urwid.ListBox(walker)
    refresh()
    view = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)
    loop = urwid.MainLoop(view, palette, unhandled_input=keystroke)
    loop.run()

    tag = ''.join(random.sample(map(chr, range(48, 57) + range(65, 90) + range(97, 122)), 32))
    tag_playbook(tag)
    run_playbook(tag)
    remove_tag(tag)

main()
