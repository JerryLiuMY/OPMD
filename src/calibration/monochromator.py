import scipy.integrate as integrate
import numpy as np
import matplotlib.pyplot as plt

R = 60000


def intensity_density(theta, lambda_over_d):
    lambda_over_a = lambda_over_d * 5
    interference_I = (np.sin(R*np.pi*theta/lambda_over_d)/(R*np.sin(np.pi*theta/lambda_over_d))+1e-4)**2
    diffraction_I = (np.sin(np.pi*theta/lambda_over_a)/(np.pi*theta/lambda_over_a)+1e-4)**2
    I = interference_I * diffraction_I
    return I


def intensity_integral(slit_width, lambda_over_d_central):
    # the range of theta permitted by the monochromator
    theta_central = lambda_over_d_central
    theta_min = theta_central * (1 - slit_width)
    theta_max = theta_central * (1 + slit_width)

    # the range of lambda that we are interested in
    lambda_over_d_max = lambda_over_d_central * (1 + 0.0002)
    lambda_over_d_min = lambda_over_d_central * (1 - 0.0002)
    lambda_over_d_all = np.linspace(lambda_over_d_min, lambda_over_d_max, num=10000)

    integral_all = []
    for lambda_over_d in lambda_over_d_all:
        integral = integrate.quad(intensity_density, theta_min, theta_max, args=(lambda_over_d))[0]
        integral_all.append(integral)
    return lambda_over_d_all, integral_all


if __name__ == '__main__':
    pass
    # lambda_over_d_central_all = [np.pi/12, np.pi/11, np.pi/10, np.pi/9, np.pi/8, np.pi/7, np.pi/6]
    # for lambda_over_d_central in lambda_over_d_central_all:
    #     lambda_over_d_all, integral_all = intensity_integral(0.05, lambda_over_d_central, 1000)
    #     plt.plot(lambda_over_d_all, integral_all)
    #     plt.show()
