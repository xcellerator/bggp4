#!/usr/bin/env python3

import sys
import hashlib

from prettytable import PrettyTable

TRACK_LENGTHS = [0] + [21]*17 + [19]*7 + [18]*6 + [17]*5
TRACK_COUNT = 35
SECTOR_SIZE = 256

class image:
    def __init__(self, binary):
        if len(binary) != 174848:
            print(f'[!] Invalid/Unsupported Size: {len(binary)}')
            exit(-1)

        self.binary = binary
        self.parse()
        return

    def parse(self):
        """Parse a D64 File"""
        self.parse_tracks()
        self.parse_bam()
        self.parse_dirs()

        self.print_file_table()

        return

    def parse_tracks(self):
        """Parse D64 Disk Image into Tracks and Sectors"""
        self.tracks = [bytearray()]

        i = 0
        for track in range(1,TRACK_COUNT+1):
            track_start = i
            track_end = track_start + ( TRACK_LENGTHS[track] * SECTOR_SIZE )
            track_data = bytearray(self.binary[track_start:track_end])

            sector_data = []
            j = 0
            for sector in range( TRACK_LENGTHS[track] ):
                sector_start = j
                sector_end = sector_start + SECTOR_SIZE
                sector_data.append( track_data[sector_start:sector_end] )
                j = sector_end

            i = track_end
            self.tracks.append( sector_data )

        return

    def parse_bam(self):
        """Parse Block Allocation Map"""
        self.bam = bam(self.tracks[18][0])
        #self.bam.print()
        return

    def parse_dirs(self):
        """Parse Directory Entries"""
        self.files = []

        for sector in self.tracks[18]:
            if sector == self.tracks[18][0]:
                continue

            for i in range(8):
                new_file = file(sector[i*32:(i+1)*32])
                self.files.append( new_file )
                if new_file._next_dir_sector == 0x0 and new_file._next_dir_track == 0x0:
                    break

            # Extra catch to break outer loop
            if new_file._next_dir_sector == 0x0 and new_file._next_dir_track == 0x0:
                break

        return

    def print_file_table(self):
        """Print the list of files on the disk with sha256sum"""
        title = f'Files on Disk "{self.bam.disk_name}"'
        field_names = ['Filename', 'Sector(s)', 'Track', 'Sector', 'Sha256Sum']
        rows = []

        for entry in self.files:
            track = entry._first_track
            sector = entry._first_sector
            if track == 0:
                break
            content = self.tracks[track][sector]

            h = hashlib.sha256()

            data = self.tracks[track][sector]
            data = data[ 2:2+data[1]-1 ]

            h.update( data )

            rows.append( [entry.name, entry._file_size, entry._first_track, entry._first_sector, h.hexdigest()] )

        table = PrettyTable()
        table.title = title
        table.field_names = field_names
        for row in rows:
            table.add_row(row)
        print(table)
        return

class file:
    def __init__(self, binary=None):
        if binary != None:
            self.binary = binary
            self.parse()
        return

    def parse(self):
        """Parse a file's directory entry"""
        i = 0

        self._next_dir_track = int.from_bytes( self.binary[i:i+2], 'little' )
        self._next_dir_sector = self._next_dir_track >> 8
        self._next_dir_track &= 0xff
        i += 2

        self._flags = self.binary[i]
        i += 1
        self._generate_flag_string()

        self._first_track = int.from_bytes( self.binary[i:i+2], 'little' )
        self._first_sector = self._first_track >> 8
        self._first_track &= 0xff
        i += 2

        self.name = self.binary[i:i+16].rstrip(b'\xa0').decode('latin-1')
        i += 16

        self._first_side_track = int.from_bytes( self.binary[i:i+2], 'little' )
        self._first_side_sector = self._first_side_track >> 8
        self._first_side_track &= 0xff
        i += 2

        self._rel = self.binary[i]
        i += 1

        # unused
        i += 6

        self._file_size = int.from_bytes( self.binary[i:i+2], 'little' )
        return

    def _generate_flag_string(self):
        """Generate a string to describe the file's flags"""
        bits = self._flags
        self._flag_string = '|'

        if bits & (1<<7):
            self._flag_string += ' Closed |'
        else:
            self._flag_string += '        |'

        if bits & (1<<6):
            self._flag_string += ' Locked |'
        else:
            self._flag_string += '        |'

        if bits & (1<<5):
            self._flag_string += '  Save  |'
        else:
            self._flag_string += '        |'

        if bits == 0b0_000_0000:
            self._flag_string += ' Scratched  |'
        elif bits & 0b1_000_0000:
            self._flag_string += ' Deleted    |'
        elif bits & 0b1_000_0001:
            self._flag_string += ' Sequential |'
        elif bits & 0b1_000_0010:
            self._flag_string += ' Program    |'
        elif bits & 0b1_000_0011:
            self._flag_string += ' User       |'
        elif bits & 0b1_000_0100:
            self._flag_string += ' Rel        |'

        return

class bam:
    def __init__(self, binary=None):
        if binary != None:
            self.binary = binary
            self.parse()
        return

    def print(self):
        """Print the Block Allocation Map to a table"""
        title = 'Block Allocation Map'
        field_names = ['Field', 'Value']

        rows = []
        rows.append( ['First Directory Sector', hex(self._first_directory_sector)] )
        rows.append( ['DOS Version', hex(self._dos_version)] )
        rows.append( ['Disk Name', f'"{self.disk_name}"'] )
        rows.append( ['Disk ID', hex(self.disk_id)] )
        rows.append( ['DOS Type', hex(self.dos_type)] )


        for i in range(1,len(self.bam_entries)):
            entry = self.bam_entries[i]
            rows.append( [f'BAM Entry {i}',f'{entry["sectors"]} (Free: {entry["free"]})'] )

        table = PrettyTable()
        table.title = title
        table.field_names = field_names
        for row in rows:
            table.add_row(row)
        print(table)

        return

    def parse(self):
        """Parse the Block Allocation Map"""

        # Header
        self.parse_bam_header()

        # BAM Entry for each track
        self.bam_entries = [[]]
        for track in range(1,TRACK_COUNT+1):
            self.parse_bam_entry(track)

        # Disk Name
        self.disk_name = self.binary[0x90:0xa0].rstrip(b'\xa0').decode('latin-1')

        # Disk ID
        self.disk_id = int.from_bytes( self.binary[0xa2:0xa4], 'little' )

        # DOS Type
        self.dos_type = int.from_bytes( self.binary[0xa5:0xa7], 'little' )
        return

    def parse_bam_header(self):
        """Parse the Block Allocation Map Header"""
        i = 0

        # Location Of First Directory Sector
        self._first_directory_sector = int.from_bytes( self.binary[i:i+2], 'little' )
        i += 2

        # DOS Version
        self._dos_version = int.from_bytes( self.binary[i:i+2], 'little' )
        i += 2

        return

    def parse_bam_entry(self, track):
        """Parse a single Block Allocation Map Entry"""
        track = track - 1
        entry_start = 0x4 + (track * 0x4)
        entry_end = entry_start + 0x4
        entry = self.binary[entry_start:entry_end]

        parsed = {}
        parsed['free'] = entry[0]
        parsed['sectors'] = []
        
        # Sectors 0-7
        bitfield = entry[1]
        parsed['sectors'].append( (bitfield & (1<<0)) >> 0 )
        parsed['sectors'].append( (bitfield & (1<<1)) >> 1 )
        parsed['sectors'].append( (bitfield & (1<<2)) >> 2 )
        parsed['sectors'].append( (bitfield & (1<<3)) >> 3 )
        parsed['sectors'].append( (bitfield & (1<<4)) >> 4 )
        parsed['sectors'].append( (bitfield & (1<<5)) >> 5 )
        parsed['sectors'].append( (bitfield & (1<<6)) >> 6 )
        parsed['sectors'].append( (bitfield & (1<<7)) >> 7 )

        # Sectors 8-15
        bitfield = entry[2]
        parsed['sectors'].append( (bitfield & (1<<0)) >> 0 )
        parsed['sectors'].append( (bitfield & (1<<1)) >> 1 )
        parsed['sectors'].append( (bitfield & (1<<2)) >> 2 )
        parsed['sectors'].append( (bitfield & (1<<3)) >> 3 )
        parsed['sectors'].append( (bitfield & (1<<4)) >> 4 )
        parsed['sectors'].append( (bitfield & (1<<5)) >> 5 )
        parsed['sectors'].append( (bitfield & (1<<6)) >> 6 )
        parsed['sectors'].append( (bitfield & (1<<7)) >> 7 )

        # Sectors 16+
        bitfield = entry[3]
        parsed['sectors'].append( (bitfield & (1<<0)) >> 0 )
        if track <= 30:
            parsed['sectors'].append( (bitfield & (1<<1)) >> 1 )
        if track <= 24:
            parsed['sectors'].append( (bitfield & (1<<2)) >> 2 )
        if track <= 17:
            parsed['sectors'].append( (bitfield & (1<<3)) >> 3 )
            parsed['sectors'].append( (bitfield & (1<<4)) >> 4 )

        self.bam_entries.append( parsed )

        return

if __name__ == '__main__':
    try:
        with open(sys.argv[1], 'rb') as f:
            binary = f.read()
    except (IndexError, FileNotFoundError) as e:
        print(f'[!] Error: {type(e)} -- {e}')
        exit(-1)

    obj = image(binary)
