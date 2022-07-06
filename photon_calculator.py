fraction_of_photons_on_sensor = 0.001481
shunt_resistor = 33000
inv_elementary_charge = 6.24150907 * 10**18


def calculate_flux(DAC_steps):
    pwm_voltage = 3.3 * DAC_steps / 65535
    current_through_led = pwm_voltage / shunt_resistor
    photon_flux_sensor = current_through_led * inv_elementary_charge * fraction_of_photons_on_sensor

    return int(photon_flux_sensor)


if __name__ == '__main__':
    print(calculate_flux(50) / 10 ** 6)


# NEPOMUC main beam           10^11       d=1cm       1.3 *10^9 p/s*mm2         2.34 *10^10 p/s (on sensor)
# NEPOMUC moderated beam      10^9        d=5mm       5 *10^7 p/s*mm2           9 *10^8 p/s
# MLL beam                    10^5        d=1mm       1.3 *10^5 p/s*mm2         2.34 *10^6 p/s