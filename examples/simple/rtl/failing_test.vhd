library ieee;
use ieee.std_logic_1164.all;

entity FailingTest is
end FailingTest;

architecture test of FailingTest is
begin
  process
  begin
    report "This should fail";
    wait for 2 ns;

    assert False;
    wait for 2 ns;

    wait;
  end process;

end test;
