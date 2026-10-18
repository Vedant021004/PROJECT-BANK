"""
generate_movies_csv.py
Utility script to write data/movies.csv cleanly with proper CSV quoting.
"""

import csv
import os

MOVIES = [
    (1, "The Grand Budapest Hotel", "Comedy", "English", "Happy", 99, 8.1, "Disney+", 2014, "A whimsical comedy about a legendary concierge and his trusted lobby boy at a famous European resort."),
    (2, "Spider-Man: Into the Spider-Verse", "Animation", "English", "Excited", 117, 8.4, "Netflix", 2018, "Teen Miles Morales becomes the new Spider-Man and joins alternate-universe heroes to stop a multiverse threat."),
    (3, "Interstellar", "Sci-Fi", "English", "Thoughtful", 169, 8.7, "Paramount+", 2014, "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."),
    (4, "Parasite", "Thriller", "Korean", "Thoughtful", 132, 8.5, "Max", 2019, "Greed and class discrimination threaten the newly formed symbiotic relationship between two contrasting families."),
    (5, "Amélie", "Romance", "French", "Happy", 122, 8.3, "Prime Video", 2001, "An imaginative Parisian waitress decides to quietly orchestrate happiness for those around her."),
    (6, "Spirited Away", "Animation", "Japanese", "Relaxed", 125, 8.6, "Max", 2001, "A young girl wanders into a world ruled by gods, witches, and spirits where humans are turned into beasts."),
    (7, "3 Idiots", "Comedy", "Hindi", "Happy", 170, 8.4, "Prime Video", 2009, "Two friends search for their long-lost companion while revisiting their college days of rebellion and discovery."),
    (8, "Whiplash", "Drama", "English", "Excited", 106, 8.5, "Netflix", 2014, "A promising young drummer enrolls at a cut-throat music conservatory where his ruthless instructor pushes him past his limits."),
    (9, "Inception", "Sci-Fi", "English", "Excited", 148, 8.8, "Netflix", 2010, "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea."),
    (10, "Paddington 2", "Comedy", "English", "Happy", 103, 7.8, "Prime Video", 2017, "Paddington takes up a series of odd jobs to buy a pop-up book for his aunt's birthday, only for it to be stolen."),
    (11, "Dangal", "Drama", "Hindi", "Emotional", 161, 8.3, "Netflix", 2016, "Former wrestler Mahavir Singh Phogat trains his young daughters to become world-class champions against all odds."),
    (12, "The Dark Knight", "Action", "English", "Excited", 152, 9.0, "Max", 2008, "When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest psychological tests."),
    (13, "Before Sunrise", "Romance", "English", "Thoughtful", 101, 8.1, "Apple TV+", 1995, "A young man and woman meet on a train in Europe and spend one unforgettable evening together in Vienna."),
    (14, "La La Land", "Romance", "English", "Emotional", 128, 8.0, "Netflix", 2016, "While navigating their careers in Los Angeles, a pianist and an actress fall in love while pursuing their passions."),
    (15, "Everything Everywhere All at Once", "Sci-Fi", "English", "Excited", 139, 7.8, "Prime Video", 2022, "A middle-aged Chinese immigrant is swept up into an insane adventure across bizarre parallel realities."),
    (16, "My Neighbor Totoro", "Animation", "Japanese", "Relaxed", 86, 8.1, "Max", 1988, "Two sisters move to the countryside to be near their ailing mother and encounter friendly forest spirits."),
    (17, "Knives Out", "Mystery", "English", "Thoughtful", 130, 7.9, "Netflix", 2019, "A quirky master detective investigates the sudden death of the patriarch of an eccentric, combative family."),
    (18, "Zindagi Na Milegi Dobara", "Drama", "Hindi", "Relaxed", 155, 8.2, "Netflix", 2011, "Three childhood friends embark on a bachelor road trip across Spain that forces each to confront past fears."),
    (19, "Mad Max: Fury Road", "Action", "English", "Excited", 120, 8.1, "Max", 2015, "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland."),
    (20, "A Silent Voice", "Animation", "Japanese", "Emotional", 130, 8.1, "Netflix", 2016, "A former bully seeks redemption and tries to make amends with a deaf girl he once tormented in grade school."),
    (21, "Cinema Paradiso", "Drama", "Italian", "Emotional", 155, 8.5, "Paramount+", 1988, "A filmmaker recalls his childhood when he fell in love with the pictures at the village cinema and befriended the projectionist."),
    (22, "Coco", "Animation", "English", "Emotional", 105, 8.4, "Disney+", 2017, "Aspiring musician Miguel confronts his family's ancestral ban on music and enters the Land of the Dead to find his great-grandfather."),
    (23, "Arrival", "Sci-Fi", "English", "Thoughtful", 116, 7.9, "Paramount+", 2016, "A linguist works with the military to communicate with alien lifeforms after mysterious spacecraft touch down across the globe."),
    (24, "Soul", "Animation", "English", "Thoughtful", 100, 8.0, "Disney+", 2020, "After landing the gig of a lifetime, a New York jazz pianist suddenly finds himself trapped in the Great Before."),
    (25, "Taare Zameen Par", "Drama", "Hindi", "Emotional", 165, 8.3, "Netflix", 2007, "An 8-year-old boy is thought to be lazy and trouble-maker, until an unconventional art teacher discovers his dyslexia."),
    (26, "Superbad", "Comedy", "English", "Happy", 113, 7.6, "Netflix", 2007, "Two co-dependent high school seniors attempt to score alcohol for a party to impress their respective crushes."),
    (27, "Your Name", "Animation", "Japanese", "Emotional", 106, 8.4, "Crunchyroll", 2016, "Two teenagers share a profound, magical connection upon discovering they are swapping bodies across space and time."),
    (28, "Shutter Island", "Thriller", "English", "Thoughtful", 138, 8.2, "Netflix", 2010, "A U.S. Marshal investigates the mysterious disappearance of a murderess who escaped from a hospital for the criminally insane."),
    (29, "The Intouchables", "Comedy", "French", "Happy", 112, 8.5, "Prime Video", 2011, "After he becomes a quadriplegic from a paragliding accident, an aristocrat hires a young man from the projects to be his caregiver."),
    (30, "Andhadhun", "Thriller", "Hindi", "Excited", 139, 8.2, "Netflix", 2018, "A series of mysterious events unfold after a blind pianist inadvertently witnesses the murder of an aging film star."),
    (31, "John Wick", "Action", "English", "Excited", 101, 7.4, "Peacock", 2014, "An ex-hit-man comes out of retirement to track down the gangsters who took everything from him."),
    (32, "Little Miss Sunshine", "Comedy", "English", "Happy", 101, 7.8, "Disney+", 2006, "A family determined to get their young daughter into the finals of a beauty pageant takes a cross-country trip in their VW bus."),
    (33, "Pan's Labyrinth", "Fantasy", "Spanish", "Thoughtful", 118, 8.2, "Prime Video", 2006, "In post-Civil War Spain, a young girl discovers a mythical overgrown labyrinth and a faun who presents her with three trials."),
    (34, "Kahaani", "Mystery", "Hindi", "Thoughtful", 122, 8.1, "Prime Video", 2012, "A pregnant woman arrives in Kolkata from London to search for her missing husband, uncovering a deadly conspiracy."),
    (35, "Midnight in Paris", "Romance", "English", "Relaxed", 94, 7.6, "Prime Video", 2011, "While on a trip to Paris with his fiancée's family, a nostalgic screenwriter finds himself mysteriously going back to the 1920s."),
    (36, "Train to Busan", "Thriller", "Korean", "Excited", 118, 7.6, "Prime Video", 2016, "While a zombie virus breaks out in South Korea, passengers struggle to survive on the bullet train from Seoul to Busan."),
    (37, "About Time", "Romance", "English", "Emotional", 123, 7.8, "Netflix", 2013, "At the age of 21, Tim discovers he can travel in time and change what happens in his own life to win the heart of the girl he loves."),
    (38, "Fantastic Mr. Fox", "Animation", "English", "Happy", 87, 7.9, "Disney+", 2009, "An urbane fox cannot resist returning to his farm-raiding ways and must help his community survive the farmers' retaliation."),
    (39, "The Lunchbox", "Drama", "Hindi", "Relaxed", 104, 7.8, "Prime Video", 2013, "A mistaken delivery in Mumbai's famously efficient lunchbox delivery system connects a lonely housewife to an older man."),
    (40, "The Truman Show", "Drama", "English", "Thoughtful", 103, 8.2, "Paramount+", 1998, "An insurance salesman discovers his entire life is actually an immensely popular round-the-clock reality TV broadcast."),
    (41, "Roma", "Drama", "Spanish", "Thoughtful", 135, 7.7, "Netflix", 2018, "A year in the life of a middle-class family's maid in Mexico City against a backdrop of domestic turmoil and political protest."),
    (42, "Singin' in the Rain", "Comedy", "English", "Happy", 103, 8.3, "Max", 1952, "A silent film star falls for a chorus girl just as he and his delusional screen partner are attempting to make the transition to talking pictures."),
    (43, "Memories of Murder", "Crime", "Korean", "Thoughtful", 132, 8.1, "Hulu", 2003, "In 1986 rural South Korea, two detectives with radically different methods struggle to catch the nation's first serial killer."),
    (44, "Gangs of Wasseypur", "Crime", "Hindi", "Excited", 160, 8.2, "Netflix", 2012, "A clash between Sultan and Shahid Khan leads to the expulsion of Khan from Wasseypur, igniting a deadly multi-generation feud."),
    (45, "Crouching Tiger Hidden Dragon", "Action", "Mandarin", "Relaxed", 120, 7.9, "Max", 2000, "A young Chinese warrior steals a sword from a famed swordsman and embarks on an adventure with a mysterious man in the frontier."),
    (46, "Ponyo", "Animation", "Japanese", "Happy", 101, 7.6, "Max", 2008, "A five-year-old boy develops a relationship with Ponyo, a goldfish princess who yearns desperately to become a human girl."),
    (47, "A Quiet Place", "Thriller", "English", "Excited", 90, 7.5, "Paramount+", 2018, "In a post-apocalyptic world, a family is forced to live in silence while hiding from blind monsters with ultra-sensitive hearing."),
    (48, "Before Sunset", "Romance", "English", "Thoughtful", 80, 8.1, "Apple TV+", 2004, "Nine years after Jesse and Celine first met in Vienna, they unexpectedly cross paths again in Paris for one afternoon."),
    (49, "Stree", "Comedy", "Hindi", "Excited", 128, 7.5, "Netflix", 2018, "In the small town of Chanderi, men live in fear of an evil spirit named Stree who abducts men during the festive season."),
    (50, "Modern Times", "Comedy", "English", "Happy", 87, 8.5, "Max", 1936, "The Little Tramp struggles to live in modern industrial society with the help of a young homeless woman."),
    (51, "The Secret in Their Eyes", "Mystery", "Spanish", "Thoughtful", 129, 8.2, "Prime Video", 2009, "A retired legal counselor writes a novel hoping to find closure for one of his unresolved homicide cases and his unreciprocated love."),
    (52, "Queen", "Comedy", "Hindi", "Happy", 144, 8.1, "Netflix", 2014, "A Delhi girl from a traditional family sets out on a solo honeymoon to Paris and Amsterdam after her fiancé calls off the wedding."),
    (53, "Drishyam", "Thriller", "Hindi", "Thoughtful", 163, 8.2, "Disney+ Hotstar", 2015, "When an unexpected crime threatens his family, a sharp cable operator uses cinema techniques to fabricate an unshakeable alibi."),
    (54, "Drishyam 2", "Thriller", "Hindi", "Excited", 140, 8.2, "Prime Video", 2022, "Seven years after the fateful case was closed, new evidence resurfaces and forces Vijay Salgaonkar to safeguard his family once more."),
    (55, "Tumbbad", "Fantasy", "Hindi", "Excited", 104, 8.2, "Prime Video", 2018, "A mythological horror fantasy following a greedy man searching for hidden gold cursed by the goddess of prosperity in rural Maharashtra."),
    (56, "Drishyam", "Thriller", "Malayalam", "Thoughtful", 160, 8.3, "Disney+ Hotstar", 2013, "Georgekutty orchestrates a labyrinth of deceptive alibis inspired by movies to protect his family after a tragic accidental crime."),
    (57, "Kantara", "Action", "Kannada", "Excited", 148, 8.2, "Netflix", 2022, "When greed paves the way for betrayal and wrath, a young tribal champion takes up arms to protect his ancestral forest and demigod traditions."),
    (58, "Sholay", "Action", "Hindi", "Excited", 162, 8.1, "Prime Video", 1975, "Two ex-convicts are hired by a former police officer to bring down the ruthless bandit Gabbar Singh.")
]

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    csv_file = os.path.join(out_dir, "movies.csv")
    
    headers = ["movie_id", "title", "genre", "language", "mood", "duration", "rating", "ott_platform", "release_year", "description"]
    
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for row in MOVIES:
            writer.writerow(row)
            
    print(f"Successfully generated {csv_file} with {len(MOVIES)} properly quoted movie rows.")

if __name__ == "__main__":
    main()
