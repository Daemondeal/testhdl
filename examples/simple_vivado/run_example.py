from testhdl import TestHDL

th = TestHDL.from_args()

th.set_simulator("vivado")

work = th.add_library("work")
work.add_systemverilog_sources("./rtl/test.sv", "./rtl/failing_test.sv")

th.add_test("Test")
th.add_test("FailingTest")

th.run()
