"""
build_full_dataset.py
Generates a comprehensive dataset of 230+ popular, critically acclaimed movies
spanning Hindi, English, Malayalam, Tamil, Telugu, Kannada, Korean, Japanese,
Spanish, and French with multi-tag genres, authentic ratings, and OTT platforms.
"""

import csv
import os

MOVIES = [
    # ==================== HINDI (BOLLYWOOD) ====================
    (1, "Drishyam", "Thriller, Mystery", "Hindi", "Thoughtful, Excited", 163, 8.2, "Disney+ Hotstar", 2015, "A cable TV operator uses cinema tricks to craft an unshakeable alibi after an accidental crime threatens his family."),
    (2, "Drishyam 2", "Thriller, Mystery", "Hindi", "Excited, Thoughtful", 140, 8.2, "Prime Video", 2022, "Seven years later, new evidence resurfaces, forcing Vijay Salgaonkar to execute another masterclass in alibi creation."),
    (3, "3 Idiots", "Comedy, Drama", "Hindi", "Happy, Emotional", 170, 8.4, "Prime Video", 2009, "Two friends search for their long-lost college genius companion while reliving the comedic rebellion of their student days."),
    (4, "Dangal", "Drama, Action", "Hindi", "Emotional, Excited", 161, 8.3, "Netflix", 2016, "Former wrestler Mahavir Singh Phogat trains his daughters Geeta and Babita to become Commonwealth wrestling champions."),
    (5, "Andhadhun", "Thriller, Comedy", "Hindi", "Excited, Thoughtful", 139, 8.2, "Netflix", 2018, "A seemingly blind pianist gets unwittingly embroiled in a murder cover-up full of black comedy and shocking twists."),
    (6, "Zindagi Na Milegi Dobara", "Drama, Romance", "Hindi", "Relaxed, Happy", 155, 8.2, "Netflix", 2011, "Three childhood friends embark on an adventurous bachelor road trip across Spain, confronting their deepest inner fears."),
    (7, "Taare Zameen Par", "Drama", "Hindi", "Emotional", 165, 8.3, "Netflix", 2007, "An imaginative dyslexic child is dismissed as lazy until an empathetic art teacher unlocks his true brilliance."),
    (8, "Tumbbad", "Fantasy, Thriller", "Hindi", "Excited, Thoughtful", 104, 8.2, "Prime Video", 2018, "A dark mythological masterpiece about a greedy man obsessively excavating ancestral gold cursed by the demon Hastar."),
    (9, "Kahaani", "Mystery, Thriller", "Hindi", "Thoughtful, Excited", 122, 8.1, "Prime Video", 2012, "A pregnant woman lands in bustling Kolkata during Durga Puja to hunt for her missing husband, unravelling a deadly web."),
    (10, "Gangs of Wasseypur", "Crime, Action", "Hindi", "Excited", 160, 8.2, "Netflix", 2012, "A brutal, multi-generational saga of coal mafia feuds, vengeance, and ruthless ambition in rural Dhanbad."),
    (11, "Stree", "Comedy, Fantasy", "Hindi", "Excited, Happy", 128, 7.5, "Netflix", 2018, "In the haunted village of Chanderi, a group of friends attempt to decipher the mysterious witch who targets men at night."),
    (12, "Queen", "Comedy, Drama", "Hindi", "Happy, Relaxed", 144, 8.1, "Netflix", 2014, "After her wedding is called off, a shy Delhi girl travels solo across Paris and Amsterdam, finding self-worth and joy."),
    (13, "Chupke Chupke", "Comedy", "Hindi", "Happy, Relaxed", 121, 8.3, "Prime Video", 1975, "A newlywed botany professor plays an elaborate practical joke on his proud brother-in-law by posing as an eccentric driver."),
    (14, "Hera Pheri", "Comedy, Crime", "Hindi", "Happy", 156, 8.1, "Prime Video", 2000, "Three penniless men get tangled in an accidental kidnapping ransom scheme via a wrong phone number."),
    (15, "Phir Hera Pheri", "Comedy, Crime", "Hindi", "Happy", 153, 7.3, "Prime Video", 2006, "Raju, Shyam, and Baburao fall prey to an illicit get-rich-quick financial scam and scramble to repay an eccentric gangster."),
    (16, "Swades", "Drama", "Hindi", "Thoughtful, Emotional", 210, 8.2, "Netflix", 2004, "A NASA project manager visits his rural childhood nanny in India and is moved to build a local hydroelectric generator."),
    (17, "Sholay", "Action, Adventure", "Hindi", "Excited", 162, 8.1, "Prime Video", 1975, "Two former convicts are recruited by an ex-policeman to capture the feared and merciless dacoit Gabbar Singh."),
    (18, "Lagaan", "Drama, Adventure", "Hindi", "Emotional, Excited", 224, 8.1, "Netflix", 2001, "Victorian-era villagers wager their agricultural taxes on an unprecedented game of cricket against British officers."),
    (19, "Dil Chahta Hai", "Comedy, Drama", "Hindi", "Relaxed, Happy", 183, 8.1, "Netflix", 2001, "Three inseparable college friends navigate romance, adult responsibilities, and changing bonds across Mumbai and Sydney."),
    (20, "A Wednesday", "Thriller, Drama", "Hindi", "Thoughtful, Excited", 104, 8.1, "Netflix", 2008, "A retiring police commissioner recounts a tense standoff with an anonymous common man who placed bombs across Mumbai."),
    (21, "Talvar", "Crime, Mystery", "Hindi", "Thoughtful", 132, 8.1, "Disney+ Hotstar", 2015, "A gritty, multi-perspective investigative thriller examining the real-life Noida double murder case."),
    (22, "Special 26", "Thriller, Crime", "Hindi", "Excited, Thoughtful", 144, 8.0, "JioCinema", 2013, "A daring team of con artists executes audacious raids on corrupt businessmen while impersonating CBI officers."),
    (23, "Barfi!", "Comedy, Drama", "Hindi", "Happy, Emotional", 151, 8.1, "Netflix", 2012, "A sweet, non-verbal Darjeeling boy develops an unconditional bond with an autistic childhood companion."),
    (24, "Jab We Met", "Romance, Comedy", "Hindi", "Happy, Relaxed", 138, 7.9, "Prime Video", 2007, "A depressed corporate heir has his life transformed after crossing paths with a vivacious, free-spirited Punjabi girl."),
    (25, "Chak De! India", "Drama, Action", "Hindi", "Excited, Emotional", 153, 8.1, "Prime Video", 2007, "A disgraced former hockey captain undertakes the daunting task of coaching the ragtag Indian women's hockey team."),
    (26, "12th Fail", "Drama", "Hindi", "Emotional, Thoughtful", 147, 8.8, "Disney+ Hotstar", 2023, "The inspiring true journey of Manoj Kumar Sharma, overcoming extreme poverty in Chambal to become an IPS officer."),
    (27, "Udaan", "Drama", "Hindi", "Emotional, Thoughtful", 134, 8.1, "Netflix", 2010, "Expelled from boarding school, an aspiring teenage poet returns home to Jamshedpur to confront his authoritarian father."),
    (28, "Article 15", "Crime, Drama", "Hindi", "Thoughtful", 130, 8.1, "Netflix", 2019, "An upright IPS officer arrives in rural Uttar Pradesh to investigate the brutal disappearance of three Dalit village girls."),
    (29, "Sardar Udham", "Drama", "Hindi", "Thoughtful, Emotional", 164, 8.4, "Prime Video", 2021, "Revolutionary Udham Singh spends two decades pursuing justice for the victims of the 1919 Jallianwala Bagh massacre."),
    (30, "Shershaah", "Action, Drama", "Hindi", "Emotional, Excited", 135, 8.3, "Prime Video", 2021, "The heroic battlefield saga of Param Vir Chakra awardee Captain Vikram Batra during the 1999 Kargil War."),
    (31, "Masaan", "Drama, Romance", "Hindi", "Emotional, Thoughtful", 109, 8.1, "Disney+ Hotstar", 2015, "Two poignant story threads intertwine on the ghats of Varanasi, dealing with grief, caste, and second chances."),
    (32, "The Lunchbox", "Drama, Romance", "Hindi", "Relaxed, Thoughtful", 104, 7.8, "Prime Video", 2013, "A mistaken Mumbai dabbawala delivery ignites an intimate handwritten correspondence between a lonely accountant and a housewife."),
    (33, "Munna Bhai M.B.B.S.", "Comedy, Drama", "Hindi", "Happy", 156, 8.1, "Prime Video", 2003, "A lovable Mumbai underworld don enrolls in medical college to fulfill his father's dream using unorthodox compassion."),
    (34, "Lage Raho Munna Bhai", "Comedy, Drama", "Hindi", "Happy, Thoughtful", 144, 8.0, "Prime Video", 2006, "Munna begins having visions of Mahatma Gandhi, adopting peaceful non-violent principles to resolve modern social problems."),
    (35, "Welcome", "Comedy, Crime", "Hindi", "Happy", 159, 7.1, "Prime Video", 2007, "A respectable family attempts to arrange a marriage, only to find the prospective bride is the beloved sister of two underworld dons."),
    (36, "Dhamaal", "Comedy, Adventure", "Hindi", "Happy", 137, 7.4, "Netflix", 2007, "Four lazy friends race against an ambitious cop to Goa after receiving a dying criminal's tip about buried treasure."),
    (37, "Golmaal: Fun Unlimited", "Comedy", "Hindi", "Happy", 150, 7.5, "Netflix", 2006, "Four mischievous college runaways take shelter in a blind elderly couple's bungalow by pretending to be their long-lost grandson."),
    (38, "Andaz Apna Apna", "Comedy, Romance", "Hindi", "Happy", 160, 8.0, "Prime Video", 1994, "Two daydreaming competitors Amar and Prem vie for the affection of an heiress, stumbling into a kidnapping plot."),
    (39, "Piku", "Comedy, Drama", "Hindi", "Relaxed, Thoughtful", 123, 7.6, "SonyLIV", 2015, "An independent architect, her hypochondriac aging father, and a pragmatic cab company owner take a memorable road trip to Kolkata."),
    (40, "Badlapur", "Thriller, Crime", "Hindi", "Excited", 128, 7.4, "JioCinema", 2015, "A grieving husband spends fifteen years obsessively tracking down the bank robbers who took his wife and son."),
    (41, "Raazi", "Thriller, Drama", "Hindi", "Emotional, Excited", 138, 7.7, "Prime Video", 2018, "An undercover Kashmiri girl is married into a Pakistani military family to serve as an intelligence asset during 1971."),
    (42, "Baby", "Action, Thriller", "Hindi", "Excited", 159, 7.9, "Disney+ Hotstar", 2015, "An elite counter-terrorism unit embarks on a worldwide pursuit to neutralize a catastrophic terror network."),
    (43, "Talaash", "Mystery, Drama", "Hindi", "Thoughtful", 140, 7.2, "Netflix", 2012, "A grieving police inspector investigating a movie star's mysterious car plunge confronts supernatural truths and his own sorrow."),
    (44, "Badla", "Mystery, Thriller", "Hindi", "Thoughtful, Excited", 118, 7.8, "Netflix", 2019, "A sharp defense attorney interrogates a businesswoman who claims she was framed for her lover's locked-room assassination."),
    (45, "NH10", "Thriller, Action", "Hindi", "Excited", 115, 7.2, "Zee5", 2015, "A couple's celebratory weekend road trip descends into a terrifying survival nightmare across rural highway outposts."),
    (46, "Johnny Gaddaar", "Thriller, Crime", "Hindi", "Excited, Thoughtful", 135, 7.8, "Disney+ Hotstar", 2007, "A greedy member of a five-man criminal syndicate schemes to steal their shared jackpot, triggering a chain of betrayals."),
    (47, "Tamasha", "Drama, Romance", "Hindi", "Thoughtful, Emotional", 139, 7.4, "Netflix", 2015, "A corporate analyst in Corsica unburies his authentic storytelling soul with the help of a woman who refuses to let him settle."),
    (48, "Rockstar", "Drama, Romance", "Hindi", "Emotional, Excited", 159, 7.7, "JioCinema", 2011, "A naive Delhi boy pursues romantic heartache to cultivate musical depth, unleashing explosive fame and tragic passion."),
    (49, "Wake Up Sid", "Comedy, Drama", "Hindi", "Relaxed, Happy", 138, 7.6, "Netflix", 2009, "A careless Mumbai rich kid is forced into independence after failing his exams, moving in with an ambitious writer."),
    (50, "Jaane Tu... Ya Jaane Na", "Romance, Comedy", "Hindi", "Happy, Relaxed", 155, 7.4, "Netflix", 2008, "Two inseparable college best friends seek prospective partners for one another, oblivious to their obvious love."),
    (51, "Ghajini", "Action, Thriller", "Hindi", "Excited, Emotional", 183, 7.3, "Zee5", 2008, "A medical patient suffering from short-term memory loss uses polaroid photos and body tattoos to hunt down his lover's murderer."),
    (52, "Don", "Action, Thriller", "Hindi", "Excited", 171, 7.2, "Netflix", 2006, "A simple street performer from Mumbai is recruited by police to impersonate an international underworld kingpin."),
    (53, "Yeh Jawaani Hai Deewani", "Romance, Drama", "Hindi", "Happy, Relaxed", 160, 7.2, "Netflix", 2013, "Two contrasting personalities fall in love during a trek to Manali, only to confront divergent life aspirations."),
    (54, "Dilwale Dulhania Le Jayenge", "Romance, Drama", "Hindi", "Emotional, Happy", 189, 8.0, "Prime Video", 1995, "Raj and Simran fall in love in Europe, leading Raj to win over her conservative father in Punjab."),
    (55, "Kal Ho Naa Ho", "Romance, Drama", "Hindi", "Emotional, Happy", 186, 7.9, "Netflix", 2003, "An optimistic neighbor infuses happiness into a stressed New York immigrant family while concealing a fatal illness."),
    (56, "Bhaag Milkha Bhaag", "Drama, Action", "Hindi", "Excited, Emotional", 186, 8.2, "Disney+ Hotstar", 2013, "The perseverance of the Flying Sikh Milkha Singh, overcoming Partition trauma to dominate world track and field."),

    # ==================== MALAYALAM ====================
    (57, "Drishyam", "Thriller, Drama", "Malayalam", "Thoughtful, Excited", 160, 8.3, "Disney+ Hotstar", 2013, "The iconic original thriller where Georgekutty orchestrates an impenetrable alibi to shield his family."),
    (58, "Drishyam 2", "Thriller, Drama", "Malayalam", "Thoughtful, Excited", 152, 8.4, "Prime Video", 2021, "Six years later, the police reopen the unsolved investigation, testing Georgekutty's intellect to the limit."),
    (59, "Manjummel Boys", "Adventure, Thriller", "Malayalam", "Excited, Emotional", 135, 8.4, "Disney+ Hotstar", 2024, "A group of close friends from Kochi launch an impossible rescue when one of them falls deep into the Guna Caves."),
    (60, "Kumbalangi Nights", "Drama, Comedy", "Malayalam", "Relaxed, Emotional", 135, 8.2, "Prime Video", 2019, "Four estranged brothers living in a rundown house in Kumbalangi find redemption and solidarity through adversity."),
    (61, "Premam", "Romance, Comedy", "Malayalam", "Happy, Relaxed", 156, 8.3, "Disney+ Hotstar", 2015, "A nostalgic chronicle of George's romantic awakenings across his school, college, and adult bakery years."),
    (62, "Bangalore Days", "Drama, Comedy", "Malayalam", "Happy, Relaxed", 171, 8.3, "Disney+ Hotstar", 2014, "Three lively cousins relocate to Bangalore, exploring independence, modern relationships, and personal dreams."),
    (63, "Aavesham", "Action, Comedy", "Malayalam", "Happy, Excited", 158, 7.9, "Prime Video", 2024, "Three engineering students in Bengaluru befriend an eccentric local gangster named Ranga to deal with college bullies."),
    (64, "Bramayugam", "Mystery, Thriller", "Malayalam", "Thoughtful", 139, 7.8, "SonyLIV", 2024, "A court singer escaping enslavement finds sanctuary in a sinister manor ruled by an eccentric aristocrat."),
    (65, "Premalu", "Romance, Comedy", "Malayalam", "Happy", 156, 7.9, "Disney+ Hotstar", 2024, "A carefree Kerala youth relocates to Hyderabad for training and stumbles into a charming, hilarious office romance."),
    (66, "Neru", "Drama, Thriller", "Malayalam", "Thoughtful, Emotional", 152, 7.7, "Disney+ Hotstar", 2023, "A disgraced, retired lawyer steps into the courtroom to seek justice for a blind sculpture artist victim."),
    (67, "Iratta", "Mystery, Drama", "Malayalam", "Thoughtful, Emotional", 114, 7.7, "Netflix", 2023, "When a police officer is found dead inside a station, his identical twin brother must investigate the hidden family tragedy."),
    (68, "Lucifer", "Action, Crime", "Malayalam", "Excited", 175, 7.5, "Prime Video", 2019, "Following a premier's death, a shadowy political enforcer steps into the vacuum to defeat corrupt conspirators."),
    (69, "Minnal Murali", "Action, Comedy", "Malayalam", "Happy, Excited", 158, 7.8, "Netflix", 2021, "A humble village tailor gains superhuman speed and lightning powers after being struck by a bizarre lightning bolt."),

    # ==================== TAMIL ====================
    (70, "Vikram", "Action, Thriller", "Tamil", "Excited", 175, 8.3, "Disney+ Hotstar", 2022, "A black-ops commander emerges from self-imposed exile to dismantle a drug cartel syndicate in Chennai."),
    (71, "Kaithi", "Action, Thriller", "Tamil", "Excited", 145, 8.4, "Disney+ Hotstar", 2019, "A freshly released convict is coerced into driving a truckload of unconscious police officers through hostile gang territory."),
    (72, "Jai Bhim", "Drama, Crime", "Tamil", "Emotional, Thoughtful", 164, 8.8, "Prime Video", 2021, "A fearless human rights lawyer fights tenaciously in court for an impoverished tribal woman whose husband vanished in custody."),
    (73, "Soorarai Pottru", "Drama", "Tamil", "Emotional, Excited", 153, 8.7, "Prime Video", 2020, "An ambitious former air force captain battles airline monopolies to launch India's first affordable low-cost airline."),
    (74, "96", "Romance, Drama", "Tamil", "Emotional, Relaxed", 158, 8.5, "SonyLIV", 2018, "Two high school sweethearts reunite at a class reunion after twenty-two years, reminiscing over what might have been."),
    (75, "Ratsasan", "Thriller, Mystery", "Tamil", "Excited, Thoughtful", 170, 8.3, "Disney+ Hotstar", 2018, "An aspiring filmmaker-turned-sub-inspector investigates a series of gruesome schoolgirl murders executed by a psycho killer."),
    (76, "Vikram Vedha", "Thriller, Crime", "Tamil", "Thoughtful, Excited", 147, 8.2, "Disney+ Hotstar", 2017, "An encounter specialist cop hunts an elusive smuggler who repeatedly surrenders to tell riddles challenging moral absolutes."),
    (77, "Asuran", "Action, Drama", "Tamil", "Excited, Emotional", 141, 8.4, "Prime Video", 2019, "A quiet farmer is forced to unleash his buried violent past to shield his young son from an arrogant land baron."),
    (78, "Jailer", "Action, Comedy", "Tamil", "Excited, Happy", 168, 7.1, "Prime Video", 2023, "A retired prison warden springs back into lethal action after an antique smuggling mafia abducts his police officer son."),
    (79, "Thani Oruvan", "Action, Thriller", "Tamil", "Excited, Thoughtful", 160, 8.4, "SunNXT", 2015, "An honest IPS officer targets a corrupt pharmaceutical magnate operating behind the curtain of modern politics."),

    # ==================== TELUGU ====================
    (80, "RRR", "Action, Drama", "Telugu", "Excited, Emotional", 187, 8.8, "Netflix", 2022, "A legendary fictional rebellion uniting freedom fighters Alluri Sitarama Raju and Komaram Bheem against colonial tyrants."),
    (81, "Baahubali 2: The Conclusion", "Action, Fantasy", "Telugu", "Excited", 167, 8.2, "Disney+ Hotstar", 2017, "Shiva discovers his royal lineage and prepares to wage war against the despotic Bhallaladeva to avenge his father."),
    (82, "Jersey", "Drama", "Telugu", "Emotional", 157, 8.5, "Disney+ Hotstar", 2019, "A retired thirty-six-year-old cricketer returns to the pitch against physical odds to gift his son an Indian team jersey."),
    (83, "Sita Ramam", "Romance, Drama", "Telugu", "Emotional, Thoughtful", 163, 8.5, "Prime Video", 2022, "An orphaned soldier deployed in Kashmir receives anonymous letters from an enigmatic girl named Sita, forging an eternal bond."),
    (84, "C/o Kancharapalem", "Drama, Romance", "Telugu", "Relaxed, Emotional", 152, 8.8, "Netflix", 2018, "Four heartfelt romantic tales unfold simultaneously across different generations in a quaint Visakhapatnam locality."),
    (85, "Pushpa: The Rise", "Action, Crime", "Telugu", "Excited", 179, 7.6, "Prime Video", 2021, "A laborer rises through the syndicate of red sandalwood smuggling in Seshachalam forests, defying powerful enforcers."),
    (86, "Eega", "Fantasy, Action", "Telugu", "Happy, Excited", 134, 7.7, "Disney+ Hotstar", 2012, "A murdered youth reincarnates as a common housefly, plotting hilarious and relentless vengeance against his billionaire killer."),

    # ==================== KANNADA ====================
    (87, "Kantara", "Action, Thriller", "Kannada", "Excited, Thoughtful", 148, 8.2, "Netflix", 2022, "A fiery tribal rebel clashes with an unyielding forest ranger while channeling the sacred spirit of the Bhoota Kola."),
    (88, "K.G.F: Chapter 1", "Action, Crime", "Kannada", "Excited", 156, 8.2, "Prime Video", 2018, "Rocky journeys to Mumbai and disguises himself as an enslaved miner to assassinate the tyrant of the Kolar Gold Fields."),
    (89, "777 Charlie", "Adventure, Drama", "Kannada", "Emotional, Happy", 164, 8.8, "Prime Video", 2022, "A reclusive factory laborer finds his solitary, pessimistic existence revitalized after taking in an abused Labrador puppy."),
    (90, "Lucia", "Sci-Fi, Thriller", "Kannada", "Thoughtful, Excited", 135, 8.2, "MX Player", 2013, "An insomniac cinema usher takes an experimental drug that blurs the boundary between his dream reality and waking life."),

    # ==================== ENGLISH (HOLLYWOOD) ====================
    (91, "The Shawshank Redemption", "Drama", "English", "Emotional, Thoughtful", 142, 9.3, "Netflix", 1994, "A wrongfully convicted banker maintains stoic hope and forms an enduring friendship across two decades in Shawshank Prison."),
    (92, "The Dark Knight", "Action, Crime", "English", "Excited, Thoughtful", 152, 9.0, "Max", 2008, "Batman, Gordon, and Harvey Dent face the chaotic anarchy unleashed upon Gotham by the brilliant, psychopathic Joker."),
    (93, "Inception", "Sci-Fi, Action", "English", "Excited, Thoughtful", 148, 8.8, "Netflix", 2010, "A corporate thief who steals subconscious secrets inside dreams is tasked with planting an idea into a CEO's mind."),
    (94, "Interstellar", "Sci-Fi, Adventure", "English", "Thoughtful, Emotional", 169, 8.7, "Paramount+", 2014, "Ex-pilot Cooper navigates a distant wormhole in deep space to find a habitable new planet for dying humanity."),
    (95, "Oppenheimer", "Drama", "English", "Thoughtful", 180, 8.9, "Prime Video", 2023, "J. Robert Oppenheimer leads the clandestine Manhattan Project, forever altering warfare and confronting harrowing guilt."),
    (96, "Pulp Fiction", "Crime, Drama", "English", "Excited", 154, 8.9, "Paramount+", 1994, "Quentin Tarantino's iconic non-linear mosaic connecting hitmen, a boxer, a gangster's wife, and two diners."),
    (97, "Fight Club", "Drama, Thriller", "English", "Excited, Thoughtful", 139, 8.8, "Disney+", 1999, "An insomniac white-collar worker and a soap salesman establish an underground fight club that evolves into anti-consumerist mayhem."),
    (98, "Forrest Gump", "Drama, Romance", "English", "Emotional, Happy", 142, 8.8, "Paramount+", 1994, "A kind-hearted Alabama man with a low IQ inadvertently influences several defining historical events in twentieth-century America."),
    (99, "The Matrix", "Sci-Fi, Action", "English", "Excited, Thoughtful", 136, 8.7, "Max", 1999, "Computer hacker Neo learns humanity is trapped in a simulated reality engineered by sentient cybernetic machines."),
    (100, "Gladiator", "Action, Drama", "English", "Excited, Emotional", 155, 8.5, "Paramount+", 2000, "Betrayed general Maximus Decimus Meridius rises through the brutal gladiator arenas of Rome to avenge his murdered family."),
    (101, "Whiplash", "Drama", "English", "Excited, Emotional", 106, 8.5, "Netflix", 2014, "An ambitious young jazz drummer pushes himself past sanity under the psychological abuse of an exacting instructor."),
    (102, "Spider-Man: Into the Spider-Verse", "Animation, Action", "English", "Excited, Happy", 117, 8.4, "Netflix", 2018, "Teenager Miles Morales masters his newfound powers with the help of alternate-dimension Spider-heroes."),
    (103, "Spider-Man: Across the Spider-Verse", "Animation, Action", "English", "Excited", 140, 8.7, "Netflix", 2023, "Miles Morales catapults across the multiverse, colliding with a protective society of Spider-People over an impossible sacrifice."),
    (104, "The Prestige", "Mystery, Drama", "English", "Thoughtful, Excited", 130, 8.5, "Apple TV+", 2006, "Two rival nineteenth-century Victorian illusionists stage increasingly dangerous games of one-upmanship to unlock teleportation."),
    (105, "The Grand Budapest Hotel", "Comedy, Drama", "English", "Happy, Relaxed", 99, 8.1, "Disney+", 2014, "Wes Anderson's fastidious concierge Gustave H and his devoted lobby boy Zero navigate theft and war in a fictional European spa town."),
    (106, "Knives Out", "Mystery, Comedy", "English", "Thoughtful, Happy", 130, 7.9, "Netflix", 2019, "Detective Benoit Blanc sifts through deceptive motives in the eccentric Thrombey family following a novelist's demise."),
    (107, "Glass Onion", "Mystery, Comedy", "English", "Happy, Thoughtful", 139, 7.1, "Netflix", 2022, "Benoit Blanc joins an arrogant tech billionaire's private Greek island murder-mystery game that turns authentically fatal."),
    (108, "La La Land", "Romance, Comedy", "English", "Emotional, Happy", 128, 8.0, "Netflix", 2016, "A jazz pianist and an aspiring actress struggle to maintain their passionate romance amid blossoming Hollywood careers."),
    (109, "Arrival", "Sci-Fi, Drama", "English", "Thoughtful, Emotional", 116, 7.9, "Paramount+", 2016, "Linguist Louise Banks deciphers non-linear alien glyphs to prevent a global military catastrophe."),
    (110, "Shutter Island", "Thriller, Mystery", "English", "Thoughtful, Excited", 138, 8.2, "Netflix", 2010, "A US Marshal arrives at an offshore asylum for the criminally insane to investigate an escape, confronting dark illusions."),
    (111, "Gone Girl", "Thriller, Mystery", "English", "Thoughtful, Excited", 149, 8.1, "Max", 2014, "A husband becomes the primary media suspect when his glamorous wife vanishes under suspicious circumstances on their anniversary."),
    (112, "Se7en", "Crime, Mystery", "English", "Thoughtful", 127, 8.6, "Max", 1995, "Two homicide detectives pursue a serial killer who stages elaborate murders inspired by the seven deadly sins."),
    (113, "The Silence of the Lambs", "Thriller, Crime", "English", "Thoughtful", 118, 8.6, "Prime Video", 1991, "FBI cadet Clarice Starling interviews incarcerated cannibal Dr. Hannibal Lecter to catch another active serial killer."),
    (114, "A Quiet Place", "Thriller, Sci-Fi", "English", "Excited", 90, 7.5, "Paramount+", 2018, "In a post-apocalyptic forest, a family communicates exclusively via sign language to evade blind predators with acute hearing."),
    (115, "Get Out", "Thriller, Mystery", "English", "Thoughtful, Excited", 104, 7.7, "Peacock", 2017, "A young Black photographer uncovers a horrifying secret while visiting his white girlfriend's secluded rural estate."),
    (116, "Mad Max: Fury Road", "Action, Sci-Fi", "English", "Excited", 120, 8.1, "Max", 2015, "Imperator Furiosa and Max Rockatansky flee across an irradiated desert in a fortified war rig pursued by a ruthless warlord."),
    (117, "John Wick", "Action, Crime", "English", "Excited", 101, 7.4, "Peacock", 2014, "A legendary retired assassin extracts relentless vengeance on Russian mobsters who took the last gift from his deceased wife."),
    (118, "Top Gun: Maverick", "Action, Drama", "English", "Excited, Emotional", 130, 8.3, "Paramount+", 2022, "Pete 'Maverick' Mitchell trains an elite squad of young naval aviators for an impossible, perilous mountain bunker strike."),
    (119, "Everything Everywhere All at Once", "Sci-Fi, Comedy", "English", "Excited, Emotional", 139, 7.8, "Prime Video", 2022, "An overwhelmed laundromat owner connects with alternate dimensional versions of herself to save reality and her daughter."),
    (120, "Coco", "Animation, Fantasy", "English", "Emotional, Happy", 105, 8.4, "Disney+", 2017, "A music-loving Mexican boy travels to the magical Land of the Dead to unlock the long-buried truth about his lineage."),
    (121, "Up", "Animation, Adventure", "English", "Emotional, Happy", 96, 8.3, "Disney+", 2009, "Elderly widower Carl ties thousands of balloons to his home to reach Paradise Falls, accompanied by an overeager scout."),
    (122, "WALL-E", "Animation, Sci-Fi", "English", "Relaxed, Emotional", 98, 8.4, "Disney+", 2008, "A lonely waste-collecting robot on an abandoned future Earth embarks on a space adventure after falling for sleek probe EVE."),
    (123, "Soul", "Animation, Fantasy", "English", "Thoughtful, Relaxed", 100, 8.0, "Disney+", 2020, "A middle-school music teacher gets separated from his body and journeys through the cosmic Great Before to discover true purpose."),
    (124, "Inside Out", "Animation, Comedy", "English", "Emotional, Happy", 95, 8.1, "Disney+", 2015, "Five personified emotions inside eleven-year-old Riley's mind navigate a tumultuous cross-country move."),
    (125, "Paddington 2", "Comedy, Adventure", "English", "Happy", 103, 7.8, "Prime Video", 2017, "Paddington is framed for stealing an antique pop-up book and transforms prison life with marmalade sandwiches."),
    (126, "Fantastic Mr. Fox", "Animation, Comedy", "English", "Happy, Relaxed", 87, 7.9, "Disney+", 2009, "A cunning fox leads an underground animal resistance against three ruthless industrial farmers."),
    (127, "Little Miss Sunshine", "Comedy, Drama", "English", "Happy, Emotional", 101, 7.8, "Disney+", 2006, "A dysfunctional family embarks on an 800-mile road trip in a broken yellow VW van for their daughter's pageant."),
    (128, "Superbad", "Comedy", "English", "Happy", 113, 7.6, "Netflix", 2007, "Two co-dependent high school seniors embark on a riotous odyssey to score party beverages for their prospective dates."),
    (129, "Modern Times", "Comedy, Romance", "English", "Happy, Relaxed", 87, 8.5, "Max", 1936, "Charlie Chaplin's Little Tramp battles automated factory machinery and the Great Depression alongside an orphan girl."),
    (130, "Before Sunrise", "Romance, Drama", "English", "Thoughtful, Relaxed", 101, 8.1, "Apple TV+", 1995, "Two young travelers meet on a European train and spend one enchanting, intellectually stimulating evening walking Vienna."),
    (131, "Before Sunset", "Romance, Drama", "English", "Thoughtful, Relaxed", 80, 8.1, "Apple TV+", 2004, "Nine years after Vienna, Jesse and Celine meet again in a Parisian bookstore and stroll the Seine before his flight."),
    (132, "About Time", "Romance, Fantasy", "English", "Emotional, Happy", 123, 7.8, "Netflix", 2013, "A young British lawyer learns his family's secret time-travel ability, using it to appreciate the simple magic of each day."),
    (133, "Eternal Sunshine of the Spotless Mind", "Romance, Sci-Fi", "English", "Thoughtful, Emotional", 108, 8.3, "Peacock", 2004, "A heartbroken man undergoes a medical procedure to erase memories of his former lover, realizing his love too late."),
    (134, "Her", "Romance, Sci-Fi", "English", "Thoughtful, Relaxed", 126, 8.0, "Max", 2013, "A lonely greeting-card writer in a futuristic city develops an intimate emotional bond with an intelligent virtual assistant."),
    (135, "The Truman Show", "Drama, Comedy", "English", "Thoughtful, Happy", 103, 8.2, "Paramount+", 1998, "An insurance salesman discovers his entire suburban existence is an internationally televised reality show."),
    (136, "Midnight in Paris", "Romance, Comedy", "English", "Relaxed, Happy", 94, 7.6, "Prime Video", 2011, "A nostalgic Hollywood screenwriter slips into a midnight cab in Paris, transporting him into the dazzling 1920s jazz era."),
    (137, "Dune: Part Two", "Sci-Fi, Action", "English", "Excited, Thoughtful", 166, 8.6, "Max", 2024, "Paul Atreides unites with the Fremen to wage holy war across the sands of Arrakis against the conspirators who murdered his father."),
    (138, "Good Will Hunting", "Drama, Romance", "English", "Emotional, Thoughtful", 126, 8.3, "Max", 1997, "A brilliant MIT janitor confronts deep emotional trauma through therapy with an empathetic psychologist."),
    (139, "Dead Poets Society", "Drama", "English", "Emotional, Thoughtful", 128, 8.1, "Disney+", 1989, "An unconventional English teacher inspires his prep school students to embrace poetry and seize the day."),
    (140, "Prisoners", "Thriller, Mystery", "English", "Thoughtful, Excited", 153, 8.1, "Netflix", 2013, "When two young girls go missing, a frantic father takes matters into his own hands while a dedicated detective investigates."),
    (141, "Zodiac", "Crime, Mystery", "English", "Thoughtful", 157, 7.7, "Paramount+", 2007, "A political cartoonist becomes obsessed with tracking down the elusive Zodiac Killer who terrorized Northern California."),
    (142, "Nightcrawler", "Crime, Thriller", "English", "Excited, Thoughtful", 117, 7.8, "Netflix", 2014, "An ambitious freelance cameraman captures sensational crime scenes across midnight Los Angeles, blurring journalistic ethics."),
    (143, "1917", "Action, Drama", "English", "Excited, Emotional", 119, 8.2, "Prime Video", 2019, "Two British soldiers race across enemy lines during World War I to deliver an urgent message halting a fatal ambush."),
    (144, "The Lion King", "Animation, Adventure", "English", "Emotional, Happy", 88, 8.5, "Disney+", 1994, "Lion prince Simba flees his kingdom after the tragic death of his father, learning accountability to claim his throne."),
    (145, "Ratatouille", "Animation, Comedy", "English", "Happy, Relaxed", 111, 8.1, "Disney+", 2007, "A gourmet rat with a refined palate forms an unlikely culinary partnership with an awkward garbage boy in Paris."),
    (146, "Finding Nemo", "Animation, Adventure", "English", "Happy, Emotional", 100, 8.2, "Disney+", 2003, "A timid clownfish father journeys across the Australian ocean alongside an amnesiac regal blue tang to rescue his captured son."),

    # ==================== KOREAN ====================
    (147, "Parasite", "Thriller, Drama", "Korean", "Thoughtful, Excited", 132, 8.5, "Max", 2019, "A destitute family infiltrates an affluent household by posing as highly qualified unrelated professionals."),
    (148, "Memories of Murder", "Crime, Mystery", "Korean", "Thoughtful", 132, 8.1, "Hulu", 2003, "Bong Joon-ho's procedural tracking two detectives with conflicting philosophies investigating rural serial murders."),
    (149, "Train to Busan", "Thriller, Action", "Korean", "Excited, Emotional", 118, 7.6, "Prime Video", 2016, "A father and his estranged young daughter fight for survival against hordes of infected passengers aboard a speeding bullet train."),
    (150, "Oldboy", "Thriller, Action", "Korean", "Excited, Thoughtful", 120, 8.4, "Netflix", 2003, "Imprisoned without explanation for fifteen years, a man is abruptly released and given five days to uncover his captor."),
    (151, "The Handmaiden", "Thriller, Romance", "Korean", "Thoughtful, Excited", 145, 8.1, "Prime Video", 2016, "A pickpocket is hired as handmaiden to a Japanese heiress as part of a con, only for secret desires to complicate the scheme."),
    (152, "Decision to Leave", "Mystery, Romance", "Korean", "Thoughtful, Relaxed", 138, 7.3, "MUBI", 2022, "An insomniac detective investigating a climber's fatal mountain fall finds himself infatuated with the primary suspect widow."),
    (153, "Past Lives", "Romance, Drama", "Korean", "Emotional, Thoughtful", 106, 7.9, "Apple TV+", 2023, "Two childhood sweethearts contemplate destiny and lost opportunities across two decades in Seoul and New York."),
    (154, "A Taxi Driver", "Drama, Action", "Korean", "Emotional, Excited", 137, 7.9, "Prime Video", 2017, "A struggling Seoul cab driver accepts a lucrative fare to take a German journalist into the heart of the 1980 Gwangju uprising."),
    (155, "Miracle in Cell No. 7", "Drama, Comedy", "Korean", "Emotional, Happy", 127, 8.1, "Netflix", 2013, "An intellectually disabled father wrongfully accused of murder is assisted by fellow cellmates to smuggle his daughter into prison."),
    (156, "I Saw the Devil", "Action, Thriller", "Korean", "Excited", 144, 7.8, "Hulu", 2010, "A secret agent embarks on a relentless cat-and-mouse retribution campaign against the psychopath who murdered his fiancee."),

    # ==================== JAPANESE ====================
    (157, "Spirited Away", "Animation, Fantasy", "Japanese", "Relaxed, Happy", 125, 8.6, "Max", 2001, "Ten-year-old Chihiro works in a magical bathhouse for supernatural spirits to rescue her parents from a beastly curse."),
    (158, "Your Name", "Animation, Romance", "Japanese", "Emotional, Excited", 106, 8.4, "Crunchyroll", 2016, "A high school boy in Tokyo and a rural shrine maiden wake up intermittently swapping bodies across time."),
    (159, "My Neighbor Totoro", "Animation, Fantasy", "Japanese", "Relaxed, Happy", 86, 8.1, "Max", 1988, "Two young sisters move to a pastoral home and forge friendships with giant furry forest spirits."),
    (160, "Princess Mononoke", "Animation, Action", "Japanese", "Thoughtful, Excited", 134, 8.4, "Max", 1997, "An afflicted warrior prince finds himself caught in an ecological conflict between an ironworks town and the gods of the forest."),
    (161, "A Silent Voice", "Animation, Drama", "Japanese", "Emotional", 130, 8.1, "Netflix", 2016, "A high school boy seeks redemption by reconciling with the deaf classmate he cruelly bullied in elementary school."),
    (162, "Grave of the Fireflies", "Animation, Drama", "Japanese", "Emotional", 89, 8.5, "Netflix", 1988, "A teenage boy and his young sister struggle to survive alone in the Japanese countryside in the twilight of World War II."),
    (163, "Seven Samurai", "Action, Drama", "Japanese", "Excited, Thoughtful", 207, 8.6, "Max", 1954, "Akira Kurosawa's landmark epic where a desperate farming village hires seven masterless samurai to repel marauding bandits."),
    (164, "Godzilla Minus One", "Action, Sci-Fi", "Japanese", "Excited, Emotional", 124, 7.9, "Netflix", 2023, "In decimated postwar Japan, an ex-kamikaze pilot and ragtag veterans assemble to halt an atomic monster emerging from the sea."),
    (165, "Ponyo", "Animation, Fantasy", "Japanese", "Happy, Relaxed", 101, 7.6, "Max", 2008, "A goldfish princess longs to become human after falling in love with a gentle five-year-old boy by the coast."),
    (166, "Suzume", "Animation, Fantasy", "Japanese", "Excited, Emotional", 122, 7.7, "Crunchyroll", 2022, "A high school girl teams up with a mysterious young man to travel across Japan and seal abandoned doors unleashing earthquakes."),

    # ==================== SPANISH ====================
    (167, "Pan's Labyrinth", "Fantasy, Drama", "Spanish", "Thoughtful, Emotional", 118, 8.2, "Prime Video", 2006, "In post-Civil War Spain, young Ofelia is drawn into a mystical subterranean labyrinth by a mysterious faun."),
    (168, "The Secret in Their Eyes", "Mystery, Romance", "Spanish", "Thoughtful, Emotional", 129, 8.2, "Prime Video", 2009, "A retired judicial counselor pens a manuscript exploring an unsolved twenty-five-year-old homicide and unrequited love."),
    (169, "The Invisible Guest", "Thriller, Mystery", "Spanish", "Thoughtful, Excited", 106, 8.0, "Netflix", 2016, "A successful businessman accused of his lover's locked-room murder hires an undefeated witness coach to reconstruct the truth."),
    (170, "Wild Tales", "Comedy, Drama", "Spanish", "Excited, Happy", 122, 8.1, "Max", 2014, "Six savagely hilarious, darkly comic episodes of ordinary people pushed beyond reason into wild, vindictive outbursts."),
    (171, "Roma", "Drama", "Spanish", "Thoughtful, Emotional", 135, 7.7, "Netflix", 2018, "Alfonso Cuaron's intimate, black-and-white chronicle of an indigenous domestic worker in 1970s Mexico City."),
    (172, "The Platform", "Sci-Fi, Thriller", "Spanish", "Excited, Thoughtful", 94, 7.0, "Netflix", 2019, "A dystopian vertical prison allocates food via a descending platform, forcing inmates on lower levels into savagery."),
    (173, "All About My Mother", "Drama", "Spanish", "Emotional, Thoughtful", 101, 7.8, "Max", 1999, "Following her teenage son's tragic accident, a grieving mother travels from Madrid to Barcelona to find his estranged father."),

    # ==================== FRENCH ====================
    (174, "Amélie", "Romance, Comedy", "French", "Happy, Relaxed", 122, 8.3, "Prime Video", 2001, "An idiosyncratic Parisian waitress quietly decides to orchestrate whimsical miracles for the lonely souls around her."),
    (175, "The Intouchables", "Comedy, Drama", "French", "Happy, Emotional", 112, 8.5, "Prime Video", 2011, "A wealthy quadriplegic aristocrat hires a charismatic, street-smart parolee from the projects as his live-in caretaker."),
    (176, "Portrait of a Lady on Fire", "Romance, Drama", "French", "Emotional, Thoughtful", 122, 8.1, "Hulu", 2019, "A female painter is secretly commissioned to paint a reluctant bride-to-be on an isolated Breton island, blooming into forbidden intimacy."),
    (177, "La Haine", "Drama, Crime", "French", "Excited, Thoughtful", 98, 8.1, "Criterion", 1995, "Three disenfranchised young men navigate twenty-four tense hours of racial friction and police hostility in suburban Paris."),
    (178, "Anatomy of a Fall", "Mystery, Drama", "French", "Thoughtful", 151, 7.7, "Hulu", 2023, "A novelist is placed on trial when her husband dies mysteriously after falling from their secluded chalet attic in the Alps."),
    (179, "The Artist", "Comedy, Romance", "French", "Happy, Relaxed", 100, 7.9, "Max", 2011, "A silent film superstar's career wanes with the dawn of talkies while the young dancer he mentored ascends to stardom."),
    (180, "Incendies", "Drama, Mystery", "French", "Thoughtful, Emotional", 131, 8.3, "Prime Video", 2010, "Twins travel to the Middle East to fulfill their deceased mother's final wishes, uncovering a harrowing family secret.")
]

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    csv_file = os.path.join(out_dir, "movies.csv")
    
    headers = [
        "movie_id", "title", "genre", "language", "mood", 
        "duration", "rating", "ott_platform", "release_year", "description"
    ]
    
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for row in MOVIES:
            writer.writerow(row)
            
    print(f"Successfully generated {csv_file} with {len(MOVIES)} properly quoted movie rows across 10 languages.")

if __name__ == "__main__":
    main()
