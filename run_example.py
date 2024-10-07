from testhdl import TestHDL

th = TestHDL.from_args()

th.set_simulator("questasim")

work = th.add_library("work")
work.add_vhdl_sources("./rtl/test.vhd", "./rtl/test2.vhd")

th.add_test("Test")
th.add_test("Test2")

th.run()
