`timescale 1ns/1ps

module tb_my_design;

  // Testbench signals
  reg         clk;
  reg         rst_n;
  reg  [31:0] a;
  reg  [31:0] b;
  reg  [31:0] c;
  reg         en;
  wire [31:0] y;

  // DUT instantiation
  my_design uut (
    .clk (clk),
    .rst_n (rst_n),
    .a (a),
    .b (b),
    .c (c),
    .en (en),
    .y (y)
  );

  // Clock generation
  initial begin
    clk = 0;
    forever #5 clk = ~clk;  // 100 MHz clock
  end

  // Test stimulus
  initial begin
    // Dump VCD for waveform viewing
    $dumpfile("tb_my_design.vcd");
    $dumpvars(0, tb_my_design);

    // Initialize signals
    rst_n = 0;
    en = 0;
    a = 0;
    b = 0;
    c = 0;

    // Release reset
    #10;
    rst_n = 1;

    // Although en is unused, we'll toggle it
    en = 1;

    // Test case 1
    a = 32'd10;
    b = 32'd20;
    c = 32'd3;
    #10;
    $display("Test1: a=%d b=%d c=%d => y=%d (expected 90)", a, b, c, y);

    // Test case 2
    a = 32'd100;
    b = 32'd50;
    c = 32'd2;
    #10;
    $display("Test2: a=%d b=%d c=%d => y=%d (expected 300)", a, b, c, y);

    // Test case 3
    a = 32'd1;
    b = 32'd1;
    c = 32'd1;
    #10;
    $display("Test3: a=%d b=%d c=%d => y=%d (expected 2)", a, b, c, y);

    // Test case 4 — check overflow wrap-around behavior
    a = 32'hFFFF_FFFF; // -1 in signed
    b = 32'd1;
    c = 32'd5;
    #10;
    $display("Test4: a=%h b=%d c=%d => y=%h", a, b, c, y);

    // Finish simulation
    #20;
    $finish;
  end

  // Optional monitor
  initial begin
    $monitor("Time=%0t clk=%b rst_n=%b a=%d b=%d c=%d y=%d", $time, clk, rst_n, a, b, c, y);
  end

endmodule