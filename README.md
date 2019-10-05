# polycom-recorder

Actually, this project can record not just conversations on a Polycom
conference phone, but any audio input, with sound activation.

## System Requirements

* Anything, but most usefully a Raspberry Pi.
* Some kind of audio hardware that provides an input channel.

## Usage

* Clone this repository.
* Create the `/usr/local/recorder/recordings` directory.
* Determine how to set up SoX to work with your audio hardware and
  enter the result in `recorder.py` (search for `AUDIODRIVER`).
* Arrange, in whichever manner seems most promising to you, for
  `recorder.py` to run on startup, and probably start it.
* Provide audio input. Recording will start as soon as any sound above rustling
  leaves is heard, and stop ten seconds after the last such sound.
  
## Accessing Recordings

* Recordings are stored in `/usr/local/recorder/recordings`.
* You may want to set up some kind of remote access.
* With a web server, you can make use of the `index.html` that is maintained in
  the same directory and updated after each recording ends.
* If you are in, to use an entirely contrived example, an Active Directory
  environment with a group of users that should have access to the recordings,
  and you have no immediate better idea than to put Samba and Apache on your
  Pi in order to handle authentication, you can just do:
  
      Alias / /usr/local/recorder/recordings/
      <Directory "/usr/local/recorder/recordings">
          AuthType GSSAPI
          AuthName polycom-rec
          Require unix-group DOMAIN\thisgroup
      </Directory>
      
  * For the `Require` line, you will need [mod_authz_unixgroup](https://github.com/chrullrich/mod_authz_unixgroup),
    which is a fork of a Google Code project archived to Github by a Good
    Samaritan, and which has not seen significant updates in years.
  * Or you find your own solution. I'm sure there is one.