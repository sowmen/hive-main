module my_design (
  input  wire         clk,
  input  wire         rst_n,
  input  wire [31:0]  a,
  input  wire [31:0]  b,
  input  wire [31:0]  c,
  input  wire         en,
  output wire [31:0]  y
);
  // Simple datapath: y = (a + b) * c
  wire [31:0] sum;
  wire [31:0] prod;
 
  assign sum  = a + b;
  assign prod = sum * c;
 
  // No pipeline initially
  assign y = prod;
 
endmodule