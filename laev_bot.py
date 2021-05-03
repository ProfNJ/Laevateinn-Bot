import discord
import asyncio
import re
from cmdlist import *
from discord.ext import commands
import DiscordUtils

#Client init
client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    #Main
    DM_channel = client.get_channel(831422116947165207)
    #await DM_channel.send("Hello, World!")

@client.command()
async def c(ctx, *, card_code):
    
    newCard = findByCode(str(card_code).upper())
    if (newCard == 0):
        await ctx.send('Sorry, but I cannot find cards with that code. Please remember to use [Set]-[Number] (eg. B01-028)')
        return()
    embed, pic = genCard(newCard)
    await ctx.send(file=pic, embed=embed)

@client.command()
async def rc(ctx):
    
    newCard = RandChar(ctx.message.author.id)
    if (newCard == 0):
        await ctx.send('Sorry, but I cannot find cards with that code.')
        return()
    embed, pic = genCard(newCard)
    await ctx.send(file=pic, embed=embed)

@client.command()
async def p(ctx, *, setName):
    (a, b) = openPack(setName, ctx.message.author.id)
    if (a == 0):
        await ctx.send('Sorry, but I cannot find that set.')
        return()
    embed = discord.Embed(title = "Your " + setName + " Pack", description = a)
    pic = discord.File(b, filename= "image.jpg")
    embed.set_image(url='attachment://image.jpg')
    await ctx.send(file=pic, embed=embed)

@client.command()
async def r(ctx):
    (a, b) = randPack(ctx.message.author.id)
    if (a == 0):
        await ctx.send('Sorry, but I cannot find that set.')
        return()
    embed = discord.Embed(title = "Your Random Pack", description = a)
    pic = discord.File(b, filename= "image.jpg")
    embed.set_image(url='attachment://image.jpg')
    await ctx.send(file=pic, embed=embed)

@client.command()
async def cp(ctx, *, tag):
    msg = str(tag).split(' ')
    print(msg)
    tag = msg[0]
    searchBy = re.escape(msg[1])
    (a, b) = customPack(tag, searchBy, ctx.message.author.id)
    if (a == 0):
        await ctx.send('Sorry, but I cannot find that set.')
        return()
    if (a == 1):
        await ctx.send('Sorry, but I cannot find that tag. Are you sure you used a tag listed in cmd-list?')
        return()
    if (a == 2):
        await ctx.send('Sorry, but I cannot find any cards.')
        return()
    embed = discord.Embed(title = "Your " + searchBy.capitalize() + " Pack", description = a)
    pic = discord.File(b, filename= "image.jpg")
    embed.set_image(url='attachment://image.jpg')
    await ctx.send(file=pic, embed=embed)

@client.command()
async def b(ctx):
    (a, b, c) = callBinder(ctx.message.author.id)
    if (a == 0):
        await ctx.send('Sorry, but I cannot find your Binder. You probably have not pulled any packs! You can do so with !p [Set].')
        return()
    pic = discord.File(b, filename= "image.jpg")
    pages = createPages(a, ctx, c, 'Your Binder', 'Your Cards')
    pManager = DiscordUtils.Pagination.AutoEmbedPaginator(ctx, auto_footer = True)
    await pManager.run(pages)

@client.command()
async def d(ctx):
    db = dropBinder(ctx.message.author.id)
    if (db == 0):
        await ctx.send('Sorry, but I cannot find your Binder. You probably have not pulled any packs! You can do so with !p [Set].')
        return()
    await ctx.send('Into the trash it goes!')

@client.command()
async def s(ctx, *, tag):
    msg = str(tag).split(' ')
    print(msg)
    tag = msg[0]
    searchBy = re.escape(msg[1])
    print(searchBy)
    (a, b) = binderchk(tag, searchBy, ctx.message.author.id, False)
    if (a == 0):
        await ctx.send('Sorry, but I cannot find your Binder. You probably have not pulled any packs! You can do so with !p [Set].')
        return()
    if (a == 1):
        await ctx.send('Sorry, but I cannot find that tag. Are you sure you used a tag listed in cmd-list?')
        return()
    if (a == 2):
        await ctx.send('Sorry, but I cannot find any cards.')
        return()
    pages = createPages(a, ctx, b, 'Search', 'Found Cards')
    pManager = DiscordUtils.Pagination.AutoEmbedPaginator(ctx, auto_footer = True)
    await pManager.run(pages)

@client.command()
async def sb(ctx, *, tag):
    msg = str(tag).split(' ')
    tag = msg[0]
    searchBy = re.escape(msg[1])
    (a, b) = binderchk(tag, searchBy, ctx.message.author.id, True)
    if (a == 0):
        await ctx.send('Sorry, but I cannot find your Binder. You probably have not pulled any packs! You can do so with !p [Set].')
        return()
    if (a == 1):
        await ctx.send('Sorry, but I cannot find that tag. Are you sure you used a tag listed in cmd-list?')
        return()
    print(a, b)
    pages = createPages(a, ctx, b, 'Search', 'Found Cards')
    pManager = DiscordUtils.Pagination.AutoEmbedPaginator(ctx, auto_footer = True)
    await pManager.run(pages)

@client.command()
async def t(ctx, member : discord.Member):
    #!t @Partner
    
    #Check to see if the user has a live collection
    if(verifyBinder(ctx.message.author.id) == 0):
        await ctx.send('Sorry, but I cannot find your Binder. You probably have not pulled any packs! You can do so with !p [Set].')
        return()
    #Find out if member wants to trade
    emo_Y = '🇾'
    emo_N = '🇳'
    msg = await ctx.send('{} would you like to accept this trade?'.format(member.mention))
    await msg.add_reaction('🇾')
    await msg.add_reaction('🇳')
    def check(reaction, user):   
        return user == member and str(reaction.emoji) in ['🇾', '🇳']
    #Await Response from member
    print('Checking for member')
    try:
        (reaction, user) = await client.wait_for('reaction_add', check=check, timeout= 30)
     #Accept
        if (reaction.emoji == emo_Y):
            await ctx.send('{} What card are you trading?'.format(ctx.message.author.mention))
            def check1(m):
                return m.author.id == ctx.message.author.id
            try:
                print('Checking for card')
                mes = await client.wait_for('message', timeout= 60, check=check1)
                if (mes == True):
                    print(mes.content)
                    print('card check')
                    (a, b) = binderchk(msg, 'card_code', ctx.message.author.id, True)
                    if (a == 2):
                        await ctx.send('You don not own a copy of that card.')
                        return()
                    newCard = findByCode(msg)
                    embed, pic = genCard(newCard)
                    await ctx.send(file=pic, embed=embed)
                    authCard = (newCard.get('card_code'))

            except asyncio.TimeoutError:
                await ctx.send('No Respone Given, cancelling trade.')
                return()

            await ctx.send('{} What card are you trading?'.format(member.mention))
            def check2(message):
                return user == member.id
            try:
                print('Checking for card')
                mes = await client.wait_for('message', timeout= 60, check=check2)
                
                if (mes == True):
                    print(mes.content)
                    print('card check')
                    (a, b) = binderchk(mes.content, 'card_code', member.id, True)
                    if (a == 2):
                        await ctx.send('You don not own a copy of that card.')
                        return()
                    newCard = findByCode(msg)
                    embed, pic = genCard(newCard)
                    await ctx.send(file=pic, embed=embed)
                    memCard = (newCard.get('card_code'))

            except asyncio.TimeoutError:
                await ctx.send('No Respone Given, cancelling trade.')
                return()
            
            
            
            t = trade(ctx.message.author.id, member.id, authCard, memCard)
            if (t == 0):
                await ctx.send('Traded!')
            return()
    #Deny
        elif (reaction.emoji == emo_N):
            await msg.delete()
            await ctx.send('Trade Denied')
            return()
    #Timeout
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.send('No Respone Given, cancelling trade.')
     

def createPages(a, b, c, d, e):
    pages = []
    ctx = b
    charLimit = 1024
    curItem = 0
    for x in range(c):
        temp = " "
        desc = " "
   
        pageMax = curItem + 9
        if (pageMax > c):
            pageMax =  c
    
        arr = a[curItem:pageMax]
        for n in arr:
            temp += str(n)
            if(len(temp) > charLimit):
                pageMax -= 1
                arr = a[curItem:pageMax]
                break

        for n in arr:
            desc += str(n)
        pages.append(discord.Embed(title = str(d), color = ctx.message.author.color).add_field(name = str(e), value= desc))
        curItem = pageMax
        if (pageMax == c):
            return(pages)
    return(pages)
    
def genCard(newCard):
    picPathing = "./img/" + "(" + newCard.get("set") + ")" + newCard.get("card_code") + ".jpg"
    embed = discord.Embed(title = newCard.get("name"), description = newCard.get("color") + "/" + newCard.get("job") + "/" + newCard.get("gender") + "/" + newCard.get("weapon") + "/" + newCard.get("type"), color = newCard.get("skin"))
    pic = discord.File(picPathing, filename= "image.jpg")
    embed.set_image(url='attachment://image.jpg')
    embed.add_field(name="Cost:", value= newCard.get("cost"))
    embed.add_field(name="Attack:", value= newCard.get("attack"))
    embed.add_field(name="Support:", value= newCard.get("support"))
    embed.add_field(name="Range:", value= newCard.get("range"))
    embed.add_field(name="Effect:", value= newCard.get("effect"))
    embed.add_field(name="Support Effect:", value= newCard.get("support_effect"))
    return(embed, pic)

    

#Running the Bot
client.run()