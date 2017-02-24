require 'spec_helper'
describe 'farm_dynpart' do
  context 'with default values for all parameters' do
    it { should contain_class('farm_dynpart') }
  end
end
