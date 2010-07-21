IRC CLIENT E BOT CHE USA ASYNCHAT
descrizione postuma dei sorgenti

descrizione generale: in sostanal il progetto è composto da:
una classe che si occupa di gestire il protocollo IRC, e i vari problemi di connessione e codifica
una classe che carichi i plugin e che fornisca a questi un semplice set di API
un plugin base per gestire gli eventi fondamentali
un plugin che gestisce Authentication,Authorization&Accounting
un plugin che facilita la creazionie di comandi via chat
un plugin con i comadi via chat base ( help, more etc)

cartella core: nucleo del bot, si occupa di gestire il portocollo, l'encoding, e alcune funzionalità base

aaa_stuff.py(vuoto) eventi relativi ad autenticazione, autorizzazione, acconto

base.py eventi base, come registrare il motd, rispondere ai ping, joinare i canali dopo il login

chatcommands.py(untested) eventi relativi alla ricezione e all'esecuzioni di comandi via privmsg (!help, !more etc)

irc_async.py(completa) le fondamenta. Gestisce la parte relativa al protocollo e all'encoding. notare che supporta SSL. Completamente passivo, non invia nulla di per sè. deferred_msg permette di rimandare l'invio di un messaggio.

numevents.py preso da irclib

simplebot.py nucleo centrale. permette di caricare plugins, a cui offre un'interfaccia simile a mirc ( ovvero self.kick() self.who() eccetera)

cartella lexers: non centra col bot irc, erano alcune prove di utilizzo di ply da testare con develbot

cartella plugins:

baseauth.py vecchio codice che doveva essere riciclato e messo in aaa_stuff.py

develbot.py un set di comandi con lo scopo di testare e lavorare sul contenuto della cartella lexer via irc.

cartella test: unit test (fatte abbastanza male) del codice. 
dummmyasync contiene un workaround per testare i bot senza socket.

PUNTI POCO CHIARI:
*riguardo tutta la parte per i messaggi ritardati (deferred_msg, deffered talk etc) essenzialmente lo scopo è di evitare preoccupazioni per il flooding: nel caso di una risposta multilinea deferred_msg ritorna un oggetto coroutine che può essere conservato e chiamato in seguito; invece buffer_talk conserva direttamente la coroutine a seconda del canale di destinazione.

*ogni plugin puo aggiungere campi al dizionario irc_data fornendo dei valori di defaut essenzalmente questi sono gli attributi di un'istanza IRCBot, sarebbee possibile semplificare parecchio.
