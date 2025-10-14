# import configparser as ConfigParser
# Encrypted details as passed from the user configuration -----
# Authour: Dr Robert B. Labs, 2023 TFMC - Magma Global.


from configparser import ConfigParser
import onetimepad
#
# # #Get the configparser object
config_object = ConfigParser()
config = ConfigParser()


def deobfuscate(md, ky, db, tcp):
    # inbuilt function to decrypt a message
    md = onetimepad.decrypt(md, 'random')
    ky = onetimepad.decrypt(ky, 'random')
    db = onetimepad.decrypt(db, 'random')
    tc = onetimepad.decrypt(tcp, 'random')
    return md, ky, db, tc


def obfuscate(md, ky, db, tcp):
    # inbuilt function to decrypt a message
    md = onetimepad.encrypt(md, 'random')
    ky = onetimepad.encrypt(ky, 'random')
    db = onetimepad.encrypt(db, 'random')
    tc = onetimepad.encrypt(tcp, 'random')
    return md, ky, db, tc


def load_configSQL(configFile):
    config_object.read(configFile)
    SQL = config_object["3e2e29372a3f24243c2720233c"]

    id = SQL['27120b16210c1f04']
    ky = SQL['390417323d081407']
    db = SQL['213022000d3f1707']
    tcp = SQL["2130222a0a193b25"]

    dc1, dc2, dc3, dc4 = deobfuscate(id, ky, db, tcp)
    # print('Server Decrypted Details:', dc1, dc2, dc3, dc4)
    return dc1, dc2, dc3, dc4


# Write to config.ini file -------------
def writeSQLconfig(a, b, c, d):
    info1 = a
    info2 = b
    info3 = c
    info4 = d
    d1, d2, d3, d4 = obfuscate(info1, info2, info3, info4)

    with open("C:\\synchronousGPU\\INI_Files\\checksumError.ini", 'w') as configfile:

        if not config.has_section("3e2e29372a3f24243c2720233c"):
            config.add_section("3e2e29372a3f24243c2720233c")
            config.set("3e2e29372a3f24243c2720233c", "27120b16210c1f04", d1)
            config.set("3e2e29372a3f24243c2720233c", "390417323d081407", d2)

            config.set("3e2e29372a3f24243c2720233c", "213022000d3f1707", d3)
            config.set("3e2e29372a3f24243c2720233c", "2130222a0a193b25", d4)

        config.write(configfile)

