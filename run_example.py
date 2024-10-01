from testhdl import TestHDL

th = TestHDL.from_args()

th.set_simulator("questasim")

work = th.add_library("work")
work.add_vhdl_sources("./rtl/test.vhd")

th.add_test("test_1")

th.run()
