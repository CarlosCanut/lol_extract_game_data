from riotwatcher import RiotWatcher, ApiError
import xlsxwriter
import xlrd as excelReader

# --- Dynamic Data ---
API_KEY = 'RGAPI-a2563a60-31e5-4189-b78c-1ea7d035bdbe'
game_ids = ['4545560961']
red_team = 'ROJO'
blue_team = 'AZUL'
# ---

game_duration = 0  # in seconds
totalTeamKills = 0
totalTeamGold = 0
enemyGoldBeforeMin10 = 0
enemyXpBeforeMin10 = 0
enemyCsBeforeMin10 = 0
totalJungleMinions = 0
totalTeamWards = 0

champ_ids = {}
champ_names = {}


# EXTRACT DATA FOR GAMEIDS

wb = excelReader.open_workbook('champion_id.xlsx')

sheet = wb.sheet_by_index(0)
for i in range(sheet.nrows):
    champ_ids[i] = int(sheet.cell_value(i,0))
    champ_names[i] = sheet.cell_value(i,1)
    print(champ_ids[i])
    print(champ_names[i])




# --- Excel ---
workbook = xlsxwriter.Workbook('data/players_data.xlsx')
worksheet = workbook.add_worksheet('data')

worksheet.write(0,0,'#')
worksheet.write(0,1,'team')
worksheet.write(0,2,'side')
worksheet.write(0,3,'role')
worksheet.write(0,4,'champion')
worksheet.write(0,5,'win')
worksheet.write(0,6,'kda')
worksheet.write(0,7,'kp')
worksheet.write(0,8,'FirstBlood')
worksheet.write(0,9,'FirstBloodAssist')
worksheet.write(0,10,'TowerFirstBlood')
worksheet.write(0,11,'TowerFirstBloodAssist')
worksheet.write(0,12,'TotalGold%')
worksheet.write(0,13,'TotalJungleMinions%')
worksheet.write(0,14,'TotalWards%')
worksheet.write(0,15,'AvGoldDiff<10')
worksheet.write(0,16,'AvXpDiff<10')
worksheet.write(0,17,'AvCsDiff<10')
worksheet.write(0,18,'AvWardsPlacedPerMin')
worksheet.write(0,19,'AvWardsClearedPerMin')


watcher = RiotWatcher(API_KEY)

data = watcher.match.by_id('euw1',game_ids[0])

game_duration = data['gameDuration']
print(data.keys())
print("")
print(data['participants'][3].keys())
print("")

row = 1
col = 0

for x in data['participants']:
    print("")
    print("")
    print("")
    worksheet.write(row,col,row)
    if x['teamId'] == 100:
        worksheet.write(row,col+1,blue_team)
    else:
        worksheet.write(row,col+1,red_team)
    
    worksheet.write(row,col+2,x['teamId'])
    if x['timeline']['role'] == 'SOLO' and x['timeline']['lane'] == 'TOP':
        worksheet.write(row,col+3,'TOP')
    elif x['timeline']['role'] == 'NONE' and x['timeline']['lane'] == 'JUNGLE':
        worksheet.write(row,col+3,'JUNGLE')
    elif x['timeline']['role'] == 'SOLO' and x['timeline']['lane'] == 'MIDDLE':
        worksheet.write(row,col+3,'MIDDLE')
    elif x['timeline']['role'] == 'DUO_CARRY' and x['timeline']['lane'] == 'BOTTOM':
        worksheet.write(row,col+3,'ADC')
    elif x['timeline']['role'] == 'DUO_SUPPORT' and x['timeline']['lane'] == 'BOTTOM':
        worksheet.write(row,col+3,'SUPPORT')
    
    for y in champ_ids:
        if x['championId'] == champ_ids[y]:
            print(champ_names[y])
            worksheet.write(row,col+4,champ_names[y])

    if x['stats']['win'] == True:
        worksheet.write(row,col+5,1)
    else:
        worksheet.write(row,col+5,0)
        
    
    print("     - Participant ID: ",x['participantId'])
    print("     - Team ID: ",x['teamId'])
    print("     - Position: ",x['timeline']['role'],x['timeline']['lane'])
    print("     - Win: ",x['stats']['win'])
    if x['stats']['deaths'] > 0:
        print("     - KDA: ",(x['stats']['kills']+x['stats']['assists'])/x['stats']['deaths'])
        worksheet.write(row,col+6,(x['stats']['kills']+x['stats']['assists'])/x['stats']['deaths'])
    else:
        print("     - KDA: ",x['stats']['kills']+x['stats']['assists'])
        worksheet.write(row,col+6,x['stats']['kills']+x['stats']['assists'])
    
    for players in data['participants']:
        if players['teamId'] == x['teamId']:
            # Se guarda las kills totales de su team
            totalTeamKills += players['stats']['kills']
            totalTeamGold += players['stats']['goldEarned']
            totalJungleMinions += players['stats']['neutralMinionsKilled']
            totalTeamWards += players['stats']['wardsPlaced']

        else:
            if x['timeline']['role'] == players['timeline']['role'] or x['timeline']['lane'] == players['timeline']['lane']:
                enemyGoldBeforeMin10 = players['timeline']['goldPerMinDeltas']['0-10']
                enemyXpBeforeMin10 = players['timeline']['xpPerMinDeltas']['0-10']
                enemyCsBeforeMin10 = players['timeline']['creepsPerMinDeltas']['0-10']
                

    if (x['stats']['kills']+x['stats']['assists']) != 0:
        print("     - KP: ",(((x['stats']['kills']+x['stats']['assists'])/totalTeamKills)*100),"%")    # Kill Participation = (player_kill + player_assists) / team_kills
        worksheet.write(row,col+7,(((x['stats']['kills']+x['stats']['assists'])/totalTeamKills)*100))
    else:
        print("     - KP: ",0,"%")
        worksheet.write(row,col+7,0)
    
    if x['stats']['firstBloodKill'] == True:
        worksheet.write(row,col+8,1)
    else:
        worksheet.write(row,col+8,0)
    
    if x['stats']['firstBloodAssist'] == True:
        worksheet.write(row,col+9,1)
    else:
        worksheet.write(row,col+9,0)

    if x['stats']['firstTowerKill'] == True:
        worksheet.write(row,col+10,1)
    else:
        worksheet.write(row,col+10,0)
    
    if x['stats']['firstTowerAssist'] == True:
        worksheet.write(row,col+11,1)
    else:
        worksheet.write(row,col+11,0)    
    
    worksheet.write(row,col+12,(x['stats']['goldEarned']/totalTeamGold)*100)
    worksheet.write(row,col+13,(x['stats']['neutralMinionsKilled']/totalJungleMinions)*100)
    worksheet.write(row,col+14,(x['stats']['wardsPlaced']/totalTeamWards)*100)
    worksheet.write(row,col+15,x['timeline']['goldPerMinDeltas']['0-10']-enemyGoldBeforeMin10)
    worksheet.write(row,col+16,x['timeline']['xpPerMinDeltas']['0-10']-enemyXpBeforeMin10)
    worksheet.write(row,col+17,x['timeline']['creepsPerMinDeltas']['0-10']-enemyCsBeforeMin10)
    worksheet.write(row,col+18,(x['stats']['wardsPlaced'])/(game_duration/60))
    worksheet.write(row,col+19,(x['stats']['wardsKilled'])/(game_duration/60))
        
    print("     - FB assist: ",x['stats']['firstBloodAssist'])
    print("     - FB: ",x['stats']['firstBloodKill'])
    print("     - TotalGold% (comparing to team's total): ",(x['stats']['goldEarned']/totalTeamGold)*100,"%")
    print("     - Tower FB: ",x['stats']['firstTowerKill'])
    print("     - Tower FB assist: ",x['stats']['firstTowerAssist'])
    print("     - Average gold diff before min 10: ",x['timeline']['goldPerMinDeltas']['0-10']-enemyGoldBeforeMin10)
    print("     - Average xp diff before min 10: ",x['timeline']['xpPerMinDeltas']['0-10']-enemyXpBeforeMin10)
    print("     - Average cs diff before min 10: ",x['timeline']['creepsPerMinDeltas']['0-10']-enemyCsBeforeMin10)
    print("     - TotalJungleMinions% (comparing to team's total): ",(x['stats']['neutralMinionsKilled']/totalJungleMinions)*100,"%")
    print("     - TotalWards% (comparing to team's total): ",(x['stats']['wardsPlaced']/totalTeamWards)*100,"%")
    print("     - Average Wards placed per min: ",(x['stats']['wardsPlaced'])/(game_duration/60))
    print("     - Average Wards cleared per min: ",(x['stats']['wardsKilled'])/(game_duration/60))


    """
    for teams in data['teams']:
        if teams['teamId'] == x['teamId']:
            print(teams['teamId'])
            print(data['teams'])
      """  
    
    print("")
    print("")
    print("")
    totalTeamKills = 0
    totalTeamGold = 0
    enemyGoldBeforeMin10 = 0
    enemyXpBeforeMin10 = 0
    enemyCsBeforeMin10 = 0
    totalJungleMinions = 0
    totalTeamWards = 0

    row += 1

workbook.close()
    
