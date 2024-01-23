import time
import sys
start_time = time.time()
for _ in range(10+1):
    print("Bonjour")
    sys.stdout.flush()  # Forcer l'impression immédiate
    
    
    time.sleep(1)  # Pause d'une seconde entre chaque impression
