import json

animations = {}
states = {}
info = {}

def parseValue(line):
    data = line.split('=')
    newData = []
    for section in data:
        newData.append(section.strip())

    return newData


currentAnimation = ""
with open('./CLIPPIT.acd', mode='rb') as file:
    fileData = file.read()
    fileData = fileData.decode(encoding='utf-8', errors='replace')
    lines = fileData.split('\n')

    print("Reading", len(lines), "lines")

    for i in range(len(lines)):
        line = lines[i].strip()
        if (line == "DefineInfo 0x0009"):
            for j in range(3):
                i += 1    
                data = parseValue(lines[i])
                info[data[0]] = data[1][1:-1]
        elif ("DefineAnimation" in line):
            currentAnimation = line.split(' ')[-1][1:-1]
            animations[currentAnimation] = []
            print("Found Animation:", currentAnimation)
        elif ("DefineFrame" in line):
            animationData = {"Duration": None, "Image": None, "Sound": None}

            # Get frame data
            while True:
                i += 1
                line = lines[i].strip()
                if ("Duration" in line):
                    animationData["Duration"] = int(parseValue(line)[-1]) * 10 # Convert "centisecond" into millisecond
                elif ("SoundEffect" in line):
                    animationData["Sound"] = parseValue(line)[-1][1:-1].split('\\')[-1]
                elif ("Filename" in line):
                    animationData["Image"] = parseValue(line)[-1][1:-1].split('\\')[-1]
                elif ("EndFrame" in line):
                    break

            animations[currentAnimation].append(animationData)
        elif ("DefineState" in line):
            state = line.split(' ')[-1][1:-1]
            stateAnimations = []

            while True:
                i += 1
                line = lines[i].strip()

                if ("EndState" in line):
                    break

                stateAnimations.append(parseValue(line)[-1][1:-1])
                
            states[state] = stateAnimations

        i += 1

with open('./animations.json', encoding='utf-8', mode='w') as file:
    file.write(json.dumps(animations, indent=2))

with open('./states.json', encoding='utf-8', mode='w') as file:
    file.write(json.dumps(states, indent=2))

with open('./info.json', encoding='utf-8', mode='w') as file:
    file.write(json.dumps(info, indent=2))