# how many strongholds are in each generation ring
strongholds_per_ring = [3, 6, 10, 15, 21, 28, 36, 10]

# the average distance of a stronghold in (index+1) ring
magnitude_per_ring = [2048, 5120, 8192, 11264, 14336, 17408, 20480, 23552]

# the distance ranges that strongholds generate in for (index+1) ring
sh_bounds = [
    (1280, 2816),
    (4352, 5888),
    (7424, 8960),
    (10496, 12032),
    (13568, 15104),
    (16640, 18176),
    (19712, 21248),
    (22784, 24320),
]

#colours for first 8 strongholds window
peach = "#fee5b5"
lightpeach = "#feedcc"
darkpeach = "#fecca8"

#colours for normal background
lightblue = "#cdeaf7"
buttonblue = "#99d4e9"
pressblue = "#b3deef"

#colours for when player should not leave spawn
spawngreen = "#66b266"
buttongreen = "#329932"
pressgreen = "#63AB63"

#colours for when players should leave spawn behind
spawnpurple = "#CDADF4"
buttonpurple = "#B28CE2"
presspurple = "#C69FF6"

# silly reponse list
silly_list = [
    "CONGRATULATIONS",
    "ok you don't have to\nkeep pressing next",
    "the run is over",
    "seriously please stop",
    "the x is in the top right",
    "im getting serious now",
    "do you think this is a joke",
    "you just spent hours\nfilling in minecraft portals",
    "and now this is what\nyou waste your time on?",
    "go take a shower or something",
    "ok this is the end bye",
    ":3",
]
