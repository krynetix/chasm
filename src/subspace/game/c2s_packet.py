"""
TODO:
http://wiki.minegoboom.com/index.php/UDP_Game_Protocol
http://d1st0rt.sscentral.com/packets.html
"""
from subspace.core.packet import Packet
from subspace.core.checksum import exe_checksum

class C2SPacket(Packet):
    pass

class SessionLoginVIE(C2SPacket):
    """ Original login packet -- like Cont, without the 64 byte tail. """ 
    _id = '\x09'
    _format = "B32s32sIBhxxhIII"+"12x"
    _components = ["is_new_user", "name", "password", "machine_id",
                   "connection_type", "time_zone_bias", "client_version", 
                   "exe_checksum", "code_checksum", "permission_id"]
    is_new_user = False
    name = ""
    password = ""
    machine_id = 0
    connection_type = 2     # options: 1 slow, 2 fast, 3 unknown, 4 not RAS
    time_zone_bias = 240    # 240 specifies EST
    client_version = 134    # 134 = VIE, 36-40 = Continuum
    exe_checksum = 0xF1429CE8
    code_checksum = 0x281CC948
    permission_id = 0 

class SessionLoginCont(SessionLoginVIE):
    """ 
    This has the same components as as SessionLoginVIE except it has the 64 
    byte tail. 
    """
    _id = '\x24'
    _format = SessionLoginVIE._format+"64s"
    _components = SessionLoginVIE._components + ["continuum_data"]
    client_version = 40
    exe_checksum = 444
    code_checksum = 0 
    continuum_data = ""

class SessionRegistrationForm(C2SPacket):
    _id = '\x17'
    _format = "32s64s32s24sBBBBBII40s40s" + 13*"40s"
    _components = ["name","email","city","state","sex","age","from_home",
                   "from_work","from_school","processor","unknown",
                   "windows_reg_name","windows_reg_organization"] + \
                   ["registry%d" % x for x in range(13)]
    name = ""
    email = ""
    city = ""
    state = ""
    sex = 'M'
    age = 0
    from_home = False
    from_work = False
    from_school = False
    process = 0
    unknown = 0
    windows_reg_name = ""
    windows_reg_organization = ""    

class ArenaEnter(C2SPacket):
    _id = '\x01'
    _format = "BbbhhH16s"
    _components = ["desired_ship", "filter_obscenity", "allow_audio",
                   "x_resolution", "y_resolution",
                   "arena_number", "arena_name"]
    desired_ship = 8            # [0, ... , 7, 8] : [warbird, ... , shark, spectator]
    filter_obscenity = False
    allow_audio = 1     # if 0, no remote msgs in private arenas in sg1.34.11f
    x_resolution = 1024
    y_resolution = 768
    arena_number = 0xFFFF   # 0xFFFF pub, 0xFFFD priv, or num for specific pub
    arena_name = ""         # this is only used if arena_number = 0xFFFD 

class ArenaLeave(C2SPacket):
    _id = '\x02'

class PositionWeapon(C2SPacket):
    _id = '\x03'
    _format = "bIhhBBhhHhH" # + "HHHI"  # these are "optional"
    _components = ["rotation","time","dx","y","checksum","status",
                   "x","dy","bounty","energy","weapon_info"]
                    # ["energy2", "s2c_latency", "timer", "item_info"]
    x = 0 # 0-16384 
    y = 0
    rotation =  0 # 0-63
    dx = 0
    dy = 0
    time = 0
    bounty = 0
    energy = 1
    checksum = 0
    status = 0
    # This can be fully interpreted by class subspace.game.weapon.WeaponInfo
    # and it can be quickly checked with method subspace.game.weapon.has_weapon()
    weapon_info = 0 

    # energy2 = 0
    # s2c_latency = 0
    # timer = 0
    # item_info = 0
    def calculate_checksum(self):
        self.checksum = 0
        # we only do the checksum on the first 22 bytes
        # i.e. no checksum on the ExtraPosData
        for c in self.raw()[:22]:
            self.checksum ^= ord(c)

class SufferDeath(C2SPacket):
    _id = '\x05'
    _format = "HH"
    _components = ["killer_player_id","bounty_at_death"]
    killer_player_id = 0
    bounty_at_death = 0

class ChatMessage(C2SPacket):
    _id = '\x06'
    _format = "BBh"
    _components = ["type","sound","target_player_id"]
    def message(self):
        return self.tail.rstrip('\x00')
    type = 2    # 0 green, 1 pub macro, 2 pub msg, 3 team msg, 4 p to team,
                # 5 priv, 6 red named, 7 remote priv, 8 red nameless, 9 channel 
    sound = 0
    target_player_id = 0

class Green(C2SPacket):
    _id = '\x07'
    _format = "Ihhhh"
    _components = ["time", "x", "y", "prize_number", "player_id"]
    player_id = 0
    prize_number = 0
    x = 0
    y = 0
    time = 0

class SpectatePlayer(C2SPacket):
    _id = '\x08'
    _format = "H"
    _components = ["spectated_player_id"]
    spectated_player_id = 0

class FileRequestUpdate(C2SPacket):
    _id = '\x0B'

class FileRequestMap(C2SPacket):
    _id = '\x0C'

class FileRequestNews(C2SPacket):
    _id = '\x0D'

# TODO: investigate
# class SendVoiceMessage(C2SPacket): 
# _id = '\x0E', _format = "I", _components["size"]

class SetFreq(C2SPacket):
    _id = '\x0F'
    _format = "H"
    _components = ["new_freq"]
    new_freq = 0

class SetShip(C2SPacket):
    _id = '\x18'
    _format = "B"
    _components = ["new_ship"]
    new_ship = 0 # [0, ... , 7, 8] : [warbird, ... , shark, spectator]

class SetBanner(C2SPacket):
    _id = '\x19'
    _format = "96s"
    _components = ["new_banner"]
    new_banner = "" # this contains 96 bytes of an uncompressed 12x8 bitmap

class AttachRequest(C2SPacket):
    _id = "\x10"
    _format = "H"
    _components = ["target_player_id"]
    target_player_id = 0

class FlagPickupRequest(C2SPacket):
    _id = "\x13"
    _format = "H"
    _components = ["flag_id"]
    flag_id = 0

class FlagDrop(C2SPacket):
    _id = "\x15"

# TODO: investigate
#class FileTransfer(C2SPacket):
#    _id = '\x16', _format = "16s", _components = ["filename"]

class SecurityChecksum(C2SPacket):
    _id = '\x1A'
    _format = "6I7HB"
    _components = ["weapon_count","settings_checksum","subspace_exe_checksum",
                   "map_lvl_checksum","s2c_slow_total","s2c_fast_total",
                   "s2c_slow_current","s2c_fast_current","s2c_reliable_out",
                   "ping","ping_average","ping_low","ping_high","slow_frames"]
    weapon_count = 0
    settings_checksum = 0
    subspace_exe_checksum = 0xF1429CE8
    map_lvl_checksum = 0xb7112727
    s2c_slow_total = 0
    s2c_fast_total = 0
    s2c_slow_current = 0
    s2c_fast_current = 0
    s2c_reliable_out = 0
    ping = 0
    ping_average = 0
    ping_low = 0
    ping_high = 0
    slow_frames = False

class SecurityViolation(C2SPacket):
    _id = '\x1B'
    _format = "B"
    _component = ["code"]
    code = 0
    def meaning(self):
        meanings = {
            0 : "Nothing wrong",
            1 : "Slow framerate",
            2 : "Current energy is higher than top energy",
            3 : "Top energy higher than max energy",
            4 : "Max energy without getting prizes",
            5 : "Recharge rate higher than max recharge rate",
            6 : "Max recharge rate without getting prizes",
            7 : "Too many burst used(More than you have)",
            8 : "Too many repel used",
            9 : "Too many decoy used(More than you have)",
            10 : "Too many thor used(More than you have)",
            11 : "Too many wall blocks used(More than you have)",
            12 : "Stealth on but never greened it",
            13 : "Cloak on but never greened it",
            14 : "XRadar on but never greened it",
            15 : "AntiWarp on but never greened it",
            16 : "Proximity bombs but never greened it",
            17 : "Bouncing bullets but never greened it",
            18 : "Max guns without greening",
            19 : "Max bombs without greening",
            20 : "Shields or Super on longer than possible",
            21 : "Saved ship weapon limits too high (burst/repel/etc)",
            22 : "Saved ship weapon level too high (guns/bombs)",
            23 : "Login checksum mismatch (program exited)",
            24 : "Unknown",
            25 : "Saved ship checksum mismatch",
            26 : "Softice Debugger Running",
            27 : "Data checksum mismatch",
            28 : "Parameter mismatch",
            60 : "Unknown integrity violation (High latency in Continuum)",
            }
        return meanings[self.code]

class BrickDrop(C2SPacket):
    _id = '\x1C'
    _format = "HH"
    _components = ["x","y"]
    x = 0  # tile coordinate
    y = 0  # tile coordinate

class BallPosition(C2SPacket):
    _id = '\x1F'
    _format = "BHHhhHI"
    _components = ["ball_id","x","y","dx","dy","my_player_id","time"]
    ball_id = 0
    x = 0
    y = 0
    dx = 0
    dy = 0
    my_player_id = 0
    time = 0

class BallPickupRequest(C2SPacket):
    _id = '\x20'
    _format = "BI"
    _components = ["ball_id","time"]
    ball_id = 0
    time = 0

class BallGoal(C2SPacket):
    _id = '\x21'
    _format = "BHH"
    ball_id = 0
    x = 0
    y = 0

def main():
    r = """
    03 00 56 e1 17 78 00 00 00 00 db 00 00 00 00 00
    00 00 00 00 00 00 cf 07 00 00 00 00 40 00 04 00
    """
    d = ''.join([b.decode('hex') for b in r.split()])
    p = PositionWeapon(d)
    print p.y & 0xFFFF
    print p

if __name__ == '__main__':
    main()