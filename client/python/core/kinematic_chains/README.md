# Motors config

Pour tester le code Python des moteurs :

1. Assurez-vous que le code "grbl.ino" a été téléversé sur la carte Arduino avec la CNC shield.

2. Ouvrez le terminal série de l'Arduino en tapant la commande suivante : "$$"

3. Assurez-vous que les paramètres si-dessous sont correctement configurés avant de tester les moteurs
```
$0=10
$1=25
$2=0
$3=0
$4=0
$5=0
$6=0
$10=1
$11=0.010
$12=0.002
$13=0
$20=0
$21=1
$22=1
$23=0
$24=10.000
$25=12.000
$26=250
$27=1.000
$30=1000
$31=0
$32=0
$100=10295.660
$101=3200.000
$102=3200.000
$110=10.000
$111=10.000
$112=10.000
$120=200.000
$121=10.000
$122=10.000
$130=21.000
$131=800.000
$132=800.000

```
# Test routine
Pour tester le bon fonctionnement de l'ensemble des moteurs exécuté le programmme motors_varian_634.py

    g_code = '$X' + '\n'
    motors_controller.execute_g_code(g_code)
    #
    motors_controller.initialisation_motor_slits()
    mode='G91\n'
    time.sleep(2)
    motors_controller.execute_g_code(mode)
    motors_controller.move_slits(0.065)