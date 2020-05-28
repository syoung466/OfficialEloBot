import discord
from discord.ext import commands
from Resources.buildData import champ_dict
from Resources.build_mapping import item_map, rune_map, summ_map, skill_map

async def createString(self, ctx, champ_name):

    error_emj = "<:error:715071240573943818>"
    title_str = f"**Build Information for:** *{champ_dict.get(champ_name, {}).get('name')}*"
    champ_gg_url = f"https://www.probuilds.net/champions/details/{champ_name}"
    
    master_str = f'\n**Starting Item(s)**'
    
    # Create starting items string
    st_item_str = f'\n> '
    for item in champ_dict.get(champ_name, {}).get('st_items'):
        try:
            st_item_str += (item_map.get(item) + ' ')
        except Exception as e:
            st_item_str += (error_emj + ' ')
            print(e)

    master_str += st_item_str

    # Create summoners string
    summ_str = '\n**Summoners**\n> '
    for summ in champ_dict.get(champ_name, {}).get('summoners'):
        try:
            summ_str += (summ_map.get(summ) + ' ')
        except Exception as e:
            summ_str += (error_emj + ' ')
            print(e)

    master_str += summ_str

    # Create Main Tree Rune string
    temp_str_1 = champ_dict.get(champ_name, {}).get('rune_tree')[0]
    rune_str_1 = f'\n**Primary Runes: {temp_str_1}** {rune_map.get(temp_str_1)}\n> '
    for i in range(0, 4): 
        try:
            rune = champ_dict.get(champ_name, {}).get('runes')[i]
            rune_str_1 += (rune_map.get(rune) + ' ')
        except Exception as e:
            rune_str_1 += (error_emj + ' ')
            print(e)

    master_str += rune_str_1 

    # Create Secondary Tree Rune String
    temp_str_2 = champ_dict.get(champ_name, {}).get('rune_tree')[1]
    rune_str_2 = f'\n**Secondary Runes: {temp_str_2}** {rune_map.get(temp_str_2)}\n> '
    for i in range(4, 6):
        try:
            rune = champ_dict.get(champ_name, {}).get('runes')[i]
            rune_str_2 += (rune_map.get(rune) + ' ')
        except Exception as e:
            rune_str_2 += (error_emj + ' ')
            print(e)

    master_str += rune_str_2

    # Create additional rune string
    rune_str_3 = "\n**Additional Runes**\n> "
    for i in range(6, 9):
        try:
            rune = champ_dict.get(champ_name, {}).get('runes')[i]
            rune_str_3 += (rune_map.get(rune) + ' ')
        except Exception as e:
            rune_str_3 += (error_emj + ' ')
            print(e)

    master_str += rune_str_3

    # Create build string
    build_str = "\n**Most Frequent Final Build**\n> "
    for item in champ_dict.get(champ_name, {}).get('build'):
        try:
            build = item_map.get(item)
            build_str += (build + ' ')
        except Exception as e:
            build_str += (error_emj + ' ')
            print(e)

    master_str += build_str

    # Create skill string
    skill_str = "\n**Most Frequent Skill Order**\n> "
    for skill in champ_dict.get(champ_name, {}).get('skills'):
        try:
            skill = skill_map.get(skill)
            skill_str += (skill + '>')
        except Exception as e:
            skill_str += error_emj
            print(e)

    skill_str = skill_str[:-1]
    master_str += skill_str

    # Send Embedded Title with Link
    await ctx.send(embed=discord.Embed(title=title_str, url=champ_gg_url, colour=discord.Colour(0xff005c)))
    await ctx.send(master_str)
    await ctx.send("`Builds are auto-generated via Riot's API and are subject to META changes and errors`")

  

