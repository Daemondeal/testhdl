library ieee;
use ieee.std_logic_1164.all;

entity Test is
end Test;

architecture t of Test is
begin
  process
  begin
    wait for 2 ns;
    report "Hello World";
    wait;
  end process;

end t;
