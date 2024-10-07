library ieee;
use ieee.std_logic_1164.all;

entity Test2 is
end Test2;

architecture t of Test2 is
begin
  process
  begin
    wait for 2 ns;
    report "Hello World 2";
    wait;
  end process;

end t;
