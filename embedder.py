'''
  Functionality for embedded message creation
  Creates, edits, loads, and saves embedded msg objects
  (embedded msg objects are just dictionaries)
  Can only be accessed from admins
'''

import discord
import json
import os

# Initialization
# timestamp? provider?
attributes = ['color', 'description', 'timestamp', 'title', 'type', 'title-url']
valid_dict_names = ['author', 'footer', 'image', 'thumbnail', 'video', 'fields']
valid_dict_attributes = ['name', 'url', 'value', 'icon_url', 'inline', 'text', 'proxy_url', 'width', 'height']
attribute_mappings = {
  'author': ['name', 'url', 'icon_url'],
  'footer': ['text', 'icon_url'],
  'image': ['url', 'proxy_url', 'width', 'height'],
  'thumbnail': ['url', 'proxy_url', 'width', 'height'],
  'video': ['url', 'width', 'height'],
  'fields': ['name', 'value', 'inline']
}

default_template = {
  'title': "Template Title",
  'color': 0x0be0e0,
  'description': "Template Description"
}
embed = {}

folder = 'templates'
fpath = folder + '/'

MAX_EMBED_SIZE = 6000
MAX_FIELD_LEN = 1024

def new():
  """Creates a new embed"""
  print("Creating new embed")
  global embed
  embed.clear()
  embed = default_template.copy()
  return

def preview():
  """
  Show the current state of the embedded message
  Eeturns the embedded message to be printed
  """
  print("Previewing embed")
  global embed
  return discord.Embed.from_dict(embed)

def add(attr, val):
  """
  Updates embedded msg content
  Returns true on success, false otherwise
  """
  print("Updating attribute")
  print("Attribute:",attr)
  print("Value:",val)
  
  # regular embedded attributes
  if attr in attributes:
    if attr == 'color':
      embed.update({attr: int(val, 16)})
    elif attr == 'title-url':
      embed.update({'url', val})
    else:
      embed.update({attr: val})
    return True

  # nested embedded attributes
  words = attr.split('-')
  dict_name = words[0]
  dict_attr = words[1]
  if dict_name in valid_dict_names and dict_attr in valid_dict_attributes:
    print("dict_name:", dict_name)
    print("dict_attr:", dict_attr)
    print("Original Embed:",embed)

    # check if dict name and attr are an accepted combination
    if not dict_attr in attribute_mappings[dict_name]:
      return False
    
    # update dict_name if it already exists
    if dict_name in embed.keys():
      d = embed[dict_name]
      d.update({dict_attr: val})
      embed[dict_name].update(d)
    # add new dictionary to the embed dict
    else:
      embed.update({dict_name: {dict_attr: val}})
    print("Updated embed:", embed)
    return True
  return False

def remove(attr):
  """
  Removes attr from embedded msg
  Returns true on success, false otherwise
  """
  print("Removing attribute")
  print("Attr:",attr)
  
  # regular embedded attributes
  if attr in attributes:
    if attr == 'title-url':
      attr = 'url'
    if attr in embed.keys():
      embed.pop(attr)
    return True

  # nested embedded attributes
  words = attr.split('-')
  dict_name, dict_attr = words
  if dict_name in valid_dict_names and dict_attr in valid_dict_attributes:
    # check if dict name and attr are an accepted combination
    if not dict_attr in attribute_mappings[dict_name]:
      return False
    # remove attribute from nested dictionary
    if dict_name in embed.keys():
      d = embed[dict_name]
      d.pop(dict_attr)
      embed[dict_name].update(d)
    return True

  return False

def templates():
  """
  Preview all saved templates
  Returns a list of embeds
  """
  print("Printing Templates")
  msgs = []
  # each element is a tuple of (name, Embedded message)
  for fname in os.scandir(folder):
    if fname.is_file():
      f = open(fname.path, 'r')
      js = json.load(f)
      f.close()
      msgs.append((str(fname), discord.Embed.from_dict(js)))
  print("Msgs:", msgs)
  return msgs
  
def load(fname):
  """
  Loads embedded msg from a template
  fname has no path/ext, can have spaces
  """
  # verification
  print("Loading Template")
  print("fname:", fname)
  if fname == '':
    return False
  fname += '.json'

  # opening json file and loading contents into
  # global embed object
  try:
    f = open(fpath + fname, 'r')
    print("fpath + fname:", fpath+fname)
    t = json.load(f)
    f.close()
    global embed
    embed = t.copy()
    print("embed:",embed)
    return True
  except:
    return False

def save(fname):
  """
  Save embedded msg as a template
  Overwrites existing names
  fname has no path/ext, can have spaces
  """
  # verification
  print("Saving Template")
  print('fname:', fname)
  if fname == '':
    return False
  fname += '.json'

  # saving embed dictionary to json file in templates folder
  global embed
  js = json.dumps(embed)
  f = open(fpath + fname, 'w')
  f.write(js)
  f.close()
  return True

def delete(fname):
  """Deletes saved template"""
  print("Deleting Template")
  # verification
  if fname == '':
    return False
  fname += '.json'

  # delete the local json filename in templates folder
  if os.path.exists(fpath+fname):
    os.remove(fpath+fname)
  else:
    return False
  return True

def channels(list):
  """
  List accessible servers and channels
  Returns embedded message
  """
  print("Generating accessible channels")
  e = discord.Embed(title="Accessible Channels", description="List of channels that I'm able to publish to", color = 0x55FDF9)
  e.set_footer(text="run corn?publish [channel_id] to publish the current embedded message to that channel")
  id = 0
  while id < len(list):
    channels = ''
    server = list[id][0]
    while id < len(list) and list[id][0] == server:
      channel = list[id][1]
      new_channel = 'ID: ' + str(id) + ' | Channel: ' + str(channel) + '\n'
      
      if len(channels) + len(new_channel) < MAX_FIELD_LEN:
        channels += new_channel
      else:
        e.add_field(name="Server: "+str(server), value=channels, inline=False)
        channels = new_channel
      
      id += 1
    # create a field where the title is the server name 
    # and the contents are the accessible channels with their id
    if channels != '':
      e.add_field(name="Server: "+str(server), value=channels, inline=False)
  return e

def role_list(list):
  """Returns embedded msg with pingable roles"""
  print("Generating pingable roles")
  e = discord.Embed(title="Pingable Roles", description="List of roles that I can ping", color = 0x55FDF9)
  e.set_footer(text="run corn?ping [role] [channel_id] [msg?] to publish the current embedded message to that channel")
  
  id = 0
  while id < len(list):
    roles = ''
    server = list[id][0]
    while id < len(list) and list[id][0] == server:
      role = list[id][1]
      new_role = 'Role: ' + role.name + '\n'

      if len(roles) + len(new_role) < MAX_FIELD_LEN:
        roles += new_role
      else:
        e.add_field(name="Server: "+str(server), value=roles, inline=False)
        roles = new_role
        
      id += 1
    # create a field where the title is the server name 
    # and the contents are the accessible channels with their id
    e.add_field(name="Server: "+str(server), value=roles, inline=False)
  return e

def voice_search_embed(list):
  """Search voices usable by imitate"""
  e = discord.Embed(title='Voice Search')

  results = ''
  i = 0
  while i < len(list):
    if len(results + list[i] +', ') < MAX_FIELD_LEN:
      results += list[i] + ', '
      i += 1
    else:
      e.add_field(name='Results:', value=results, inline=False)
      results = ''

  if results != '':
    e.add_field(name='Results:', value=results, inline=False)
  return e

'''
    corn?help [group]

    empty - list all help groups with desc of each
    all - list values of every group  in one message (original implementation)
    edit - new, preview, add/set, remove
    publish - publish, channels
    template - templates, load, save, delete
    attributes - all attributes, single and grouped
    misc - help, example
'''
def admin_help(group):
  """Returns embedder help (admin only)"""
  valid_groups = ['all', 'edit', 'publish', 'templates', 'attributes', 'single_attributes', 
  'grouped_attributes', 'misc']
  
  help_path = 'bot_embeds/help-'
  if group in valid_groups:
    help_path += group + '.json'
  else:
    # empty or invalid
    help_path = 'bot_embeds/help.json'

  f = open(help_path, 'r')
  help = json.load(f).copy()
  f.close()
  return discord.Embed.from_dict(help)

def server_help():
  """Returns server help embed"""
  '''corn?help - Displays this msg
      corn?hey - Get a random val quote
     corn?revive - Ping everyone with a necromancer role to revive this channel
     corn?imitate [voice] [message] - Send a tts message into a vc [admin only]
     corn?voice_search [query] - Search for a tts voice [admin only]
  '''
  f = open('bot_embeds/help-server.json', 'r')
  help = json.load(f).copy()
  f.close()
  return discord.Embed.from_dict(help)