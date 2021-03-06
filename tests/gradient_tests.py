import unittest

import tensorflow as tf
import tfdiffeq

from tests import problems
from tests.check_grad import gradcheck


eps = 1e-12

# torch.set_default_dtype(torch.float64)
TEST_DEVICE = "gpu:0" if tf.test.is_gpu_available() else "cpu:0"


def max_abs(tensor):
    return tf.reduce_max(tf.abs(tensor))


class TestGradient(unittest.TestCase):

    def test_midpoint(self):
        f, y0, t_points, _ = problems.construct_problem(TEST_DEVICE)

        func = lambda y0, t_points: tfdiffeq.odeint(f, y0, t_points, method='midpoint')
        self.assertTrue(gradcheck(func, (y0, t_points)))

    def test_rk4(self):
        f, y0, t_points, _ = problems.construct_problem(TEST_DEVICE)

        func = lambda y0, t_points: tfdiffeq.odeint(f, y0, t_points, method='rk4')
        self.assertTrue(gradcheck(func, (y0, t_points)))

    def test_dopri5(self):
        f, y0, t_points, _ = problems.construct_problem(TEST_DEVICE)

        func = lambda y0, t_points: tfdiffeq.odeint(f, y0, t_points, method='dopri5')
        self.assertTrue(gradcheck(func, (y0, t_points)))

    def test_adams(self):
        f, y0, t_points, _ = problems.construct_problem(TEST_DEVICE)

        func = lambda y0, t_points: tfdiffeq.odeint(f, y0, t_points, method='adams')
        self.assertTrue(gradcheck(func, (y0, t_points)))

    # def test_adjoint(self):
    #     """
    #     Test against dopri5
    #     """
    #     f, y0, t_points, _ = problems.construct_problem(TEST_DEVICE)
    #
    #     func = lambda y0, t_points: tfdiffeq.odeint(f, y0, t_points, method='dopri5')
    #
    #     tf.set_random_seed(0)
    #     with tf.GradientTape() as tape:
    #         tape.watch(t_points)
    #         ys = func(y0, t_points)
    #
    #     # gradys = tf.random_uniform(ys.shape)
    #     # ys.backward(gradys)
    #
    #     # reg_y0_grad = y0.grad
    #     reg_t_grad, reg_a_grad, reg_b_grad = tape.gradient(ys, [t_points, f.a, f.b])
    #     # reg_t_grad = t_points.grad
    #     # reg_a_grad = f.a.grad
    #     # reg_b_grad = f.b.grad
    #
    #     f, y0, t_points, _ = problems.construct_problem(TEST_DEVICE)
    #
    #     y0 = (y0,)
    #
    #     func = lambda y0, t_points: tfdiffeq.odeint_adjoint(f, y0, t_points, method='dopri5')
    #
    #     with tf.GradientTape() as tape:
    #         tape.watch(t_points)
    #         ys = func(y0, t_points)
    #
    #     grads = tape.gradient(ys, [t_points, f.a, f.b])
    #     adj_t_grad, adj_a_grad, adj_b_grad = grads
    #
    #     # self.assertLess(max_abs(reg_y0_grad - adj_y0_grad), eps)
    #     self.assertLess(max_abs(reg_t_grad - adj_t_grad), eps)
    #     self.assertLess(max_abs(reg_a_grad - adj_a_grad), eps)
    #     self.assertLess(max_abs(reg_b_grad - adj_b_grad), eps)


# class TestCompareAdjointGradient(unittest.TestCase):
#
#     def problem(self):
#
#         class Odefunc(tf.keras.Model):
#
#             def __init__(self):
#                 super(Odefunc, self).__init__()
#                 self.A = tf.Variable([[-0.1, 2.0], [-2.0, -0.1]], dtype=tf.float64)
#                 self.unused_module = tf.keras.layers.Dense(5)
#
#             def call(self, t, y):
#                 y = tfdiffeq.cast_double(y)
#                 return tf.matmul(y ** 3, self.A)
#
#         y0 = tf.convert_to_tensor([[2., 0.]])
#         t_points = tf.linspace(0., 25., 10)
#         func = Odefunc()
#         return func, y0, t_points
#
#     def test_dopri5_adjoint_against_dopri5(self):
#         with tf.GradientTape() as tape:
#             func, y0, t_points = self.problem()
#             # tape.watch(t_points)
#             tape.watch(y0)
#             ys = tfdiffeq.odeint_adjoint(func, y0, t_points, method='dopri5')
#
#         adj_y0_grad = tape.gradient(ys, y0)  # y0.grad
#         # adj_t_grad = tape.gradient(ys, t_points)  # t_points.grad
#         adj_A_grad = tape.gradient(ys, func.A)  # func.A.grad
#
#         print("reached here")
#         # w_grad, b_grad = tape.gradient(ys, func.unused_module.variables)
#         # self.assertEqual(max_abs(w_grad), 0)
#         # self.assertEqual(max_abs(b_grad), 0)
#
#         with tf.GradientTape() as tape:
#             func, y0, t_points = self.problem()
#             tape.watch(y0)
#             # tape.watch(t_points)
#             ys = tfdiffeq.odeint(func, y0, t_points, method='dopri5')
#
#         y_grad = tape.gradient(ys, y0)
#         # t_grad = tape.gradient(ys, t_points)
#         a_grad = tape.gradient(ys, func.A)
#
#         self.assertLess(max_abs(y_grad - adj_y0_grad), 3e-4)
#         # self.assertLess(max_abs(t_grad - adj_t_grad), 1e-4)
#         self.assertLess(max_abs(a_grad - adj_A_grad), 2e-3)

    # def test_adams_adjoint_against_dopri5(self):
    #     func, y0, t_points = self.problem()
    #     ys_ = torchdiffeq.odeint_adjoint(func, y0, t_points, method='adams')
    #     gradys = torch.rand_like(ys_) * 0.1
    #     ys_.backward(gradys)
    #
    #     adj_y0_grad = y0.grad
    #     adj_t_grad = t_points.grad
    #     adj_A_grad = func.A.grad
    #     self.assertEqual(max_abs(func.unused_module.weight.grad), 0)
    #     self.assertEqual(max_abs(func.unused_module.bias.grad), 0)
    #
    #     func, y0, t_points = self.problem()
    #     ys = torchdiffeq.odeint(func, y0, t_points, method='dopri5')
    #     ys.backward(gradys)
    #
    #     self.assertLess(max_abs(y0.grad - adj_y0_grad), 5e-2)
    #     self.assertLess(max_abs(t_points.grad - adj_t_grad), 5e-4)
    #     self.assertLess(max_abs(func.A.grad - adj_A_grad), 2e-2)


if __name__ == '__main__':
    unittest.main()
