module FailingTest;
initial begin
    $display("This test will fail");
    $error("HI");
    $finish();
end
endmodule : FailingTest
